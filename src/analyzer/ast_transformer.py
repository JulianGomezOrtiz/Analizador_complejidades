from lark import Transformer, Token


def tree_to_ast(tree):
    return ASTBuilder().transform(tree)


class ASTBuilder(Transformer):
    """Convierte el árbol de Lark en un AST basado únicamente en diccionarios.

    Diseño robusto: cada regla intenta aceptar children que sean dicts (nodos AST),
    Token (terminales) o listas (posibles resultados sin normalizar). El objetivo:
    que stmt_list devuelva siempre {"type":"Block","body":[...]}.
    """

    ############################################################################
    # UTILIDADES
    ############################################################################
    # ============================
    #   FIX: convertir raíz start
    # ============================
    def start(self, items):
        # items = [Program]
        # devolvemos directamente el diccionario Program
        if len(items) == 1 and isinstance(items[0], dict):
            return items[0]
        return items

    def _as_name(self, node):
        # Extrae el nombre de un Token o un dict Identifier o de estructuras similares
        if isinstance(node, Token):
            return str(node)
        if isinstance(node, dict):
            # Puede ser {'type':'Identifier','name':...} o {'name':...}
            if node.get("type") == "Identifier":
                return node["name"]
            if "name" in node:
                return node["name"]
        # fallback
        return str(node)

    def _to_identifier(self, token_or_node):
        if isinstance(token_or_node, dict):
            # si ya es Identifier
            if token_or_node.get("type") == "Identifier":
                return token_or_node
            if "name" in token_or_node:
                return {"type": "Identifier", "name": token_or_node["name"]}
        if isinstance(token_or_node, Token):
            return {"type": "Identifier", "name": str(token_or_node)}
        # fallback
        return {"type": "Identifier", "name": str(token_or_node)}

    def _to_number(self, token_or_node):
        if isinstance(token_or_node, dict) and token_or_node.get("type") == "Number":
            return token_or_node
        if isinstance(token_or_node, Token):
            try:
                return {"type": "Number", "value": int(token_or_node)}
            except Exception:
                try:
                    return {"type": "Number", "value": int(token_or_node.value)}
                except Exception:
                    raise
        # fallback if already a python int
        if isinstance(token_or_node, int):
            return {"type": "Number", "value": token_or_node}
        return {"type": "Number", "value": int(str(token_or_node))}

    ############################################################################
    # TERMINALES
    ############################################################################
    def IDENTIFIER(self, token):
        return {"type": "Identifier", "name": str(token)}

    def NUMBER(self, token):
        return {"type": "Number", "value": int(token)}

    ############################################################################
    # PROGRAMA
    ############################################################################
    def program(self, items):
        """Regresa {"type": "Program", "procedures": [...]}"""
        procs = [x for x in items if isinstance(
            x, dict) and x.get("type") == "Procedure"]
        return {"type": "Program", "procedures": procs}

        ###########################################################################
    #   NUEVO: convertir "routine" → dict Procedure
    ###########################################################################
    def routine(self, items):

        # ignoramos items[0] (Token PROCEDURE)
        identifier = items[1]       # dict: {"type":"Identifier","name":...}

        # nombre del procedimiento
        name = identifier["name"]

        # detectar si hay parámetros
        params = []
        block = None

        # items puede ser: [Token PROC, identifier, block]
        # o:              [Token PROC, identifier, params, block]
        for it in items[2:]:
            if isinstance(it, list):      # lista = parámetros
                params = [p for p in it if isinstance(
                    p, dict) and p.get("name")]
            elif isinstance(it, dict) and it.get("type") == "Block":
                block = it

        if block is None:
            block = {"type": "Block", "body": []}

        return {
            "type": "Procedure",
            "name": name,
            "params": params,
            "body": block["body"],
        }

    def param_list(self, items):
        """param_list: param (COMMA param)*"""
        params = []
        for x in items:
            # x puede ser dict (Identifier), Token o lista
            if isinstance(x, dict) and x.get("type") == "Identifier":
                params.append({"name": x["name"]})
            elif isinstance(x, dict) and "name" in x:
                params.append({"name": x["name"]})
            elif isinstance(x, Token):
                params.append({"name": str(x)})
            elif isinstance(x, list):
                # a veces el transform deja listas anidadas
                for y in x:
                    if isinstance(y, dict) and "name" in y:
                        params.append({"name": y["name"]})
        return params

    def param(self, items):
        # items típicamente: [IDENTIFIER] transformado ya a dict
        if len(items) and isinstance(items[0], dict) and "name" in items[0]:
            return {"name": items[0]["name"]}
        if len(items) and isinstance(items[0], Token):
            return {"name": str(items[0])}
        return {"name": str(items[0])}

    ############################################################################
    # BLOQUES Y SECUENCIAS: stmt_list devuelve SIEMPRE Block
    ############################################################################
    def stmt_list(self, items):
        """Garantiza siempre un Block."""
        stmts = []
        for x in items:
            # a veces vienen listas anidadas (por llamadas previas)
            if isinstance(x, list):
                for y in x:
                    if isinstance(y, dict):
                        stmts.append(y)
            elif isinstance(x, dict):
                stmts.append(x)
            # ignorar tokens (p.ej. ; vacíos)
        return {"type": "Block", "body": stmts}

    def block(self, items):
        # block: BEGINKW stmt_list ENDKW
        # stmt_list ya devuelve Block en nuestra implementación, así que devolvemos ese Block.
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                return it
        # si no lo encontró, construir uno:
        stmts = [x for x in items if isinstance(x, dict)]
        return {"type": "Block", "body": stmts}

    ############################################################################
    # STATEMENTS
    ############################################################################
    def assign_stmt(self, items):
        # LValue ASSIGN expr
        target = items[0]
        value = items[1] if len(items) > 1 else None
        # target puede llegar como dict LValue o Identifier -> normalizar
        if isinstance(target, dict) and target.get("type") == "LValue":
            tname = target["name"]
        elif isinstance(target, dict) and target.get("type") == "Identifier":
            tname = target["name"]
        elif isinstance(target, Token):
            tname = str(target)
        else:
            # si target es dict con "name"
            tname = target.get("name", str(target)) if isinstance(
                target, dict) else str(target)
        return {"type": "Assign", "target": {"type": "LValue", "name": tname}, "value": value}

    def lvalue(self, items):
        # lvalue: IDENTIFIER (indexing)* | field_access
        if len(items) == 0:
            return {"type": "LValue", "name": ""}
        first = items[0]
        if isinstance(first, dict) and first.get("type") == "Identifier":
            return {"type": "LValue", "name": first["name"]}
        if isinstance(first, Token):
            return {"type": "LValue", "name": str(first)}
        if isinstance(first, dict) and "name" in first:
            return {"type": "LValue", "name": first["name"]}
        return {"type": "LValue", "name": str(first)}

    def return_stmt(self, items):
        # RETURN expr?
        val = None
        if len(items) and isinstance(items[0], dict):
            val = items[0]
        elif len(items) and isinstance(items[0], Token):
            # número literal posiblemente
            try:
                val = self.NUMBER(items[0])
            except Exception:
                val = {"type": "Identifier", "name": str(items[0])}
        return {"type": "Return", "value": val}

    def call_stmt(self, items):
        # CALLKW IDENTIFIER "(" arg_list? ")"
        # items puede contener CALLKW token; buscamos el Identifier y arg_list (lista) si existe
        name = None
        args = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier" and name is None:
                name = it["name"]
            elif isinstance(it, list):
                # arg_list devolvió lista de dicts
                args = [x for x in it if isinstance(x, dict)]
        if name is None:
            # fallback: buscar primer token IDENTIFIER
            for it in items:
                if isinstance(it, Token) and it.type == "IDENTIFIER":
                    name = str(it)
                    break
        return {"type": "Call", "name": name, "args": args}

    def arg_list(self, items):
        # arg_list: expr (COMMA expr)*
        # filtrar solo dicts (exprs transformados)
        args = []
        for it in items:
            if isinstance(it, dict):
                args.append(it)
            elif isinstance(it, Token):
                # puede ser NUMBER o IDENTIFIER sin transformar
                if it.type == "NUMBER":
                    args.append(self.NUMBER(it))
                else:
                    args.append({"type": "Identifier", "name": str(it)})
            elif isinstance(it, list):
                for y in it:
                    if isinstance(y, dict):
                        args.append(y)
        return args

    ############################################################################
    # COMPOUND STATEMENTS (if/for/while/repeat)
    ############################################################################
    def if_stmt(self, items):
        """if_stmt: IFKW expr THENKW stmt_list (ELSEKW stmt_list)? ENDKW"""
        # extraer dicts: los exprs y los Blocks
        cond = None
        then_block = {"body": []}
        else_block = {"body": []}

        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                if then_block["body"] == []:
                    then_block = it
                else:
                    else_block = it
            elif isinstance(it, dict) and cond is None and it.get("type") not in ("Block",):
                cond = it
            elif isinstance(it, Token) and cond is None:
                # improbable si IDENTIFIER ya transformado, pero por seguridad:
                cond = {"type": "Identifier", "name": str(it)}

        if cond is None:
            cond = {"type": "Identifier", "name": "UNKNOWN_COND"}

        return {
            "type": "If",
            "cond": cond,
            "then": then_block["body"],
            "else_": else_block["body"],
        }

    def for_stmt(self, items):
        """for_stmt: FORKW IDENTIFIER ASSIGN expr TOWK expr DOKW stmt_list ENDKW"""
        # Buscamos: identifier, start expr, end expr, block
        identifier = None
        start = None
        end = None
        block = {"body": []}

        # Extraemos dicts no-Block como candidatos a exprs/ident
        dicts = [it for it in items if isinstance(it, dict)]
        # Bloque
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                block = it
                break

        # Intentar deducir var, start, end en dicts
        # si el primer dict es Identifier -> var
        if dicts:
            if dicts[0].get("type") == "Identifier":
                identifier = dicts[0]["name"]
                # start y end serían dicts[1] y dicts[2] si existen
                if len(dicts) >= 3:
                    start = dicts[1]
                    end = dicts[2]
            else:
                # en algunos casos lvalue/identificador puede venir como {"name":...}
                first = dicts[0]
                if "name" in first and not first.get("type") == "Block":
                    identifier = first["name"]
                    if len(dicts) >= 3:
                        start = dicts[1]
                        end = dicts[2]

        # Si falta, buscar tokens
        if identifier is None:
            for it in items:
                if isinstance(it, Token) and it.type == "IDENTIFIER":
                    identifier = str(it)
                    break

        return {
            "type": "For",
            "var": identifier,
            "start": start,
            "end": end,
            "body": block["body"],
        }

    def while_stmt(self, items):
        # WHILEKW expr DOKW stmt_list ENDKW
        cond = None
        block = {"body": []}
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                block = it
            elif isinstance(it, dict) and cond is None:
                cond = it
            elif isinstance(it, Token) and cond is None:
                cond = {"type": "Identifier", "name": str(it)}
        return {"type": "While", "cond": cond, "body": block["body"]}

    def repeat_stmt(self, items):
        # REPEATKW stmt_list UNTILKW expr SEMI?
        block = {"body": []}
        cond = None
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                block = it
            elif isinstance(it, dict) and cond is None and it.get("type") != "Block":
                cond = it
            elif isinstance(it, Token) and cond is None:
                cond = {"type": "Identifier", "name": str(it)}
        return {"type": "Repeat", "cond": cond, "body": block["body"]}

    ############################################################################
    # EXPRESSIONS
    ############################################################################
    def binop(self, items):
        # arith: arith ("+"|"-") term -> binop
        # term: term ("*"|"/") factor -> binop
        # items puede venir como [left, op_token, right] o (en casos raros) [left, right]
        if len(items) == 3:
            left = items[0]
            op_token = items[1]
            right = items[2]
            if isinstance(op_token, Token):
                op = str(op_token)
            elif isinstance(op_token, dict) and "op" in op_token:
                op = op_token["op"]
            else:
                op = str(op_token)
            return {"type": "BinOp", "left": left, "op": op, "right": right}
        elif len(items) == 2:
            # caso atípico: no hay token operador (evita crash)
            left = items[0]
            right = items[1]
            return {"type": "BinOp", "left": left, "op": None, "right": right}
        else:
            # fallback: retornar primer elemento (no es realmente binop)
            return items[0] if items else {"type": "BinOp", "left": None, "op": None, "right": None}

    def cmp(self, items):
        # expr_cmp: arith ((">" | "<" | ">=" | "<=" | "=") arith)?
        if len(items) == 3:
            left = items[0]
            op_token = items[1]
            right = items[2]
            op = str(op_token) if isinstance(op_token, Token) else (
                op_token if isinstance(op_token, str) else str(op_token))
            return {"type": "Cmp", "left": left, "op": op, "right": right}
        else:
            return items[0] if items else {"type": "Cmp", "left": None, "op": None, "right": None}

    def neg(self, items):
        return {"type": "Unary", "op": "-", "expr": items[0]}

    def pos(self, items):
        return {"type": "Unary", "op": "+", "expr": items[0]}

    def or_expr(self, items):
        return {"type": "LogicOp", "op": "or", "left": items[0], "right": items[1]}

    def and_expr(self, items):
        return {"type": "LogicOp", "op": "and", "left": items[0], "right": items[1]}

    ############################################################################
    # ATOMS, CALLS, ARRAYS, INDEXING, FIELDS
    ############################################################################
    def call_expr(self, items):
        # IDENTIFIER function_call
        # items: [Identifier, arg_list?]
        name = None
        args = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier" and name is None:
                name = it["name"]
            elif isinstance(it, list):
                args = [x for x in it if isinstance(x, dict)]
        return {"type": "Call", "name": name, "args": args}

    def function_call(self, items):
        # "(" arg_list? ")"
        # Lark pasa args (si existen) como lista
        if items and isinstance(items[0], list):
            return items[0]
        return []

    def array_expr(self, items):
        # IDENTIFIER indexing+
        # items: [Identifier, expr, expr, ...] o [Identifier, [expr,...]]
        name = None
        indexes = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier" and name is None:
                name = it["name"]
            elif isinstance(it, dict) and it.get("type") != "Identifier":
                # items could be expressions
                indexes.append(it)
            elif isinstance(it, list):
                for y in it:
                    if isinstance(y, dict):
                        indexes.append(y)
            elif isinstance(it, Token) and name is None:
                name = str(it)
        return {"type": "ArrayExpr", "name": name, "indexes": indexes}

    def var(self, items):
        # var: IDENTIFIER
        if items and isinstance(items[0], dict) and items[0].get("type") == "Identifier":
            return items[0]
        if items and isinstance(items[0], Token):
            return {"type": "Identifier", "name": str(items[0])}
        return {"type": "Identifier", "name": str(items[0])}

    def indexing(self, items):
        # "[" expr "]" -> recibiremos el expr transformado
        if items:
            return items[0]
        return None

    def field_access(self, items):
        # IDENTIFIER "." IDENTIFIER
        left = items[0]
        right = items[-1]
        left_name = left["name"] if isinstance(
            left, dict) and "name" in left else str(left)
        right_name = right["name"] if isinstance(
            right, dict) and "name" in right else str(right)
        return {"type": "FieldAccess", "object": left_name, "field": right_name}
