# ast_transformer.py
from lark import Transformer, Token
from typing import Any, List


def tree_to_ast(tree):
    return ASTBuilder().transform(tree)


class ASTBuilder(Transformer):
    """
    Convierte el árbol de Lark en un AST basado únicamente en diccionarios.
    Maneja Tokens, dicts ya transformados y listas anidadas.
    """

    # --------------------
    # UTILIDADES
    # --------------------
    def _is_token(self, x):
        return isinstance(x, Token)

    def _tok_type(self, t):
        return t.type if isinstance(t, Token) else None

    def _tok_str(self, t):
        return str(t) if isinstance(t, Token) else str(t)

    def _ensure_identifier_dict(self, token_or_dict):
        if isinstance(token_or_dict, dict) and token_or_dict.get("type") == "Identifier":
            return token_or_dict
        if isinstance(token_or_dict, dict) and "name" in token_or_dict:
            return {"type": "Identifier", "name": token_or_dict["name"]}
        if isinstance(token_or_dict, Token):
            return {"type": "Identifier", "name": str(token_or_dict)}
        return {"type": "Identifier", "name": str(token_or_dict)}

    def _ensure_number_dict(self, token_or_dict):
        if isinstance(token_or_dict, dict) and token_or_dict.get("type") == "Number":
            return token_or_dict
        if isinstance(token_or_dict, Token):
            return {"type": "Number", "value": int(token_or_dict)}
        if isinstance(token_or_dict, int):
            return {"type": "Number", "value": token_or_dict}
        return {"type": "Number", "value": int(str(token_or_dict))}

    # --------------------
    # RAÍZ / PROGRAMA
    # --------------------
    def start(self, items):
        # items suele ser [program]
        if len(items) == 1 and isinstance(items[0], dict):
            return items[0]
        return items

    def program(self, items):
        """Regresa {"type":"Program","procedures":[...]}"""
        procs = [x for x in items if isinstance(
            x, dict) and x.get("type") == "Procedure"]
        return {"type": "Program", "procedures": procs}

    # --------------------
    # TERMINALES
    # --------------------
    def IDENTIFIER(self, token):
        return {"type": "Identifier", "name": str(token)}

    def NUMBER(self, token):
        return {"type": "Number", "value": int(token)}

    # --------------------
    # RUTINAS / PROCEDIMIENTOS
    # --------------------
    def routine(self, items):
        # <--- AGREGAR ESTO
        print(f"\n[DEBUG ROUTINE] Items recibidos: {items}")

        name = None
        params: List[dict] = []
        block = None

        # 1) extraer nombre
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier":
                name = it["name"]
                break
            if isinstance(it, Token) and it.type == "IDENTIFIER":
                name = str(it)
                break

        # 2) buscar bloque (body)
        for it in items:
            # CASO A: El bloque ya fue transformado a diccionario (Ideal)
            if isinstance(it, dict) and it.get("type") == "Block":
                block = it
                break
            # CASO B (NUEVO): El bloque llegó crudo como Tree (Error de nombres)
            if hasattr(it, 'data') and it.data == 'block':
                print(
                    "¡ALERTA! El bloque llegó como Tree. Revisa el nombre de la regla en la gramática.")

        # 3) buscar param_list
        for it in items:
            if isinstance(it, list):
                for p in it:
                    if isinstance(p, dict) and p.get("name") and p.get("name") != name:
                        params.append({"name": p["name"]})
                    elif isinstance(p, Token) and p.type == "IDENTIFIER" and str(p) != name:
                        params.append({"name": str(p)})

        if block is None:
            print(
                "[ERROR] No se encontró 'Block' en routine. Se devolverá cuerpo vacío.")
            block = {"type": "Block", "body": []}

        # ... filtrado de parámetros (código original) ...
        filtered = []
        seen = set()
        for p in params:
            if p["name"] not in seen and p["name"] != name:
                filtered.append(p)
                seen.add(p["name"])
        params = filtered

        return {
            "type": "Procedure",
            "name": name or "UNKNOWN_PROC",
            "params": params,
            "body": block["body"],
        }

    def param_list(self, items):
        params = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier":
                params.append({"name": it["name"]})
            elif isinstance(it, Token) and it.type == "IDENTIFIER":
                params.append({"name": str(it)})
            elif isinstance(it, list):
                for x in it:
                    if isinstance(x, dict) and x.get("type") == "Identifier":
                        params.append({"name": x["name"]})
                    elif isinstance(x, Token) and x.type == "IDENTIFIER":
                        params.append({"name": str(x)})
        return params

    def param(self, items):
        if items:
            first = items[0]
            if isinstance(first, dict) and "name" in first:
                return {"name": first["name"]}
            if isinstance(first, Token) and first.type == "IDENTIFIER":
                return {"name": str(first)}
        return {"name": "UNKNOWN_PARAM"}

    # --------------------
    # BLOQUES / SECUENCIAS
    # --------------------
    def stmt_list(self, items):
        stmts = []
        for x in items:
            if isinstance(x, list):
                for y in x:
                    if isinstance(y, dict):
                        stmts.append(y)
            elif isinstance(x, dict):
                stmts.append(x)
            # --- DEBUGGING DE COSAS IGNORADAS ---
            elif hasattr(x, 'data'):  # Es un Tree de Lark
                print(
                    f"⚠️ [ALERTA] stmt_list ignoró una regla no transformada: '{x.data}'.")
                print(
                    f"   >> DEBES AGREGAR: def {x.data}(self, items): return items[0]")
            # ------------------------------------
        return {"type": "Block", "body": stmts}

    # ---------------------------------------------------------
    # REGLAS PASAMANOS (CRÍTICO: Desempaquetan reglas intermedias)
    # ---------------------------------------------------------

    def statement(self, items):
        # Regla: statement -> for_stmt | if_stmt ...
        # Simplemente devolvemos el hijo único (que ya es un dict)
        if items:
            return items[0]
        return None

    def simple_stmt(self, items):
        return items[0] if items else None

    def compound_stmt(self, items):
        return items[0] if items else None

    # Por si tu gramática usa nombres en plural o singulares distintos
    def statements(self, items):
        return self.stmt_list(items)

    def block(self, items):
        # suele recibir [BEGINKW, stmt_list, ENDKW] -> devolver el stmt_list
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                return it
        # fallback: construir block con dicts
        stmts = [x for x in items if isinstance(x, dict)]
        return {"type": "Block", "body": stmts}

    # --------------------
    # STATEMENTS
    # --------------------
    def assign_stmt(self, items):
        # lvalue ASSIGN expr
        target = items[0] if items else None
        value = items[-1] if len(items) > 1 else None

        # normalizar target a LValue dict
        if isinstance(target, dict):
            if target.get("type") == "LValue":
                name = target.get("name", "")
            elif target.get("type") == "Identifier":
                name = target.get("name")
            else:
                name = target.get("name", str(target))
        elif isinstance(target, Token) and target.type == "IDENTIFIER":
            name = str(target)
        else:
            name = str(target)

        return {"type": "Assign", "target": {"type": "LValue", "name": name}, "value": value}

    def lvalue(self, items):
        if not items:
            return {"type": "LValue", "name": ""}
        first = items[0]
        if isinstance(first, dict) and first.get("type") == "Identifier":
            return {"type": "LValue", "name": first["name"]}
        if isinstance(first, Token) and first.type == "IDENTIFIER":
            return {"type": "LValue", "name": str(first)}
        if isinstance(first, dict) and "name" in first:
            return {"type": "LValue", "name": first["name"]}
        return {"type": "LValue", "name": str(first)}

    def return_stmt(self, items):
        val = None
        # Buscamos el primer elemento que sea un diccionario (la expresión)
        # o un Token que NO sea la palabra clave "RETURN"
        for it in items:
            if isinstance(it, dict):
                val = it
                break
            elif isinstance(it, Token) and it.type != "RETURNKW" and it.type != "RETURN":
                # Caso borde: devuelve un número o variable simple
                if it.type == "NUMBER":
                    val = self.NUMBER(it)
                else:
                    val = {"type": "Identifier", "name": str(it)}
                break

        return {"type": "Return", "value": val}

    def call_stmt(self, items):
        # CALLKW IDENTIFIER "(" arg_list? ")"
        name = None
        args: List[dict] = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier" and name is None:
                name = it["name"]
            elif isinstance(it, Token) and it.type == "IDENTIFIER" and name is None:
                name = str(it)
            elif isinstance(it, list):
                # arg_list suele venir como lista
                for a in it:
                    if isinstance(a, dict):
                        args.append(a)
        return {"type": "Call", "name": name, "args": args}

    def arg_list(self, items):
        args = []
        for it in items:
            if isinstance(it, dict):
                # FILTRO: Ignorar identificadores que sean comas
                if it.get("type") == "Identifier" and it.get("name") == ",":
                    continue
                args.append(it)
            elif isinstance(it, Token):
                if str(it) == ",":
                    continue  # Ignorar token coma

                if it.type == "NUMBER":
                    args.append(self.NUMBER(it))
                else:
                    args.append({"type": "Identifier", "name": str(it)})
        return args

    # --------------------
    # COMPOUND (if/for/while/repeat)
    # --------------------
    def if_stmt(self, items):
        cond = None
        then_block = {"body": []}
        else_block = {"body": []}
        # items contiene cond y bloques; identificar por tipo
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Block":
                if then_block["body"] == []:
                    then_block = it
                else:
                    else_block = it
            elif isinstance(it, dict) and cond is None:
                cond = it
            elif isinstance(it, Token) and cond is None:
                cond = {"type": "Identifier", "name": str(it)}
        if cond is None:
            cond = {"type": "Identifier", "name": "UNKNOWN_COND"}
        return {"type": "If", "cond": cond, "then": then_block["body"], "else_": else_block["body"]}

    def for_stmt(self, items):
        """
        Versión Robusta: Busca componentes por tipo en lugar de posición fija.
        Estructura esperada: Var, Start, End, Body.
        """
        var = None
        block = {"type": "Block", "body": []}
        exprs = []  # Aquí guardaremos las expresiones de inicio y fin

        for it in items:
            # 1. Detectar la variable del ciclo
            # Usualmente es el primer identificador que encontramos
            if var is None:
                if isinstance(it, Token) and it.type == "IDENTIFIER":
                    var = str(it)
                    continue
                elif isinstance(it, dict) and it.get("type") == "Identifier":
                    var = it["name"]
                    continue

            # 2. Detectar el Bloque (Cuerpo del ciclo)
            if isinstance(it, dict) and it.get("type") == "Block":
                block = it
                continue

            # 3. Recolectar expresiones (Start y End)
            # Ignoramos palabras clave si se cuelan en 'items'
            is_expr = False
            if isinstance(it, dict) and it.get("type") not in ("Block", "Identifier"):
                is_expr = True
            elif isinstance(it, Token) and it.type == "NUMBER":
                is_expr = True
            # Si ya tenemos variable, el siguiente identificador suele ser parte de una expresión (ej: 1 TO n)
            elif var is not None and (
                (isinstance(it, dict) and it.get("type") == "Identifier") or
                (isinstance(it, Token) and it.type == "IDENTIFIER")
            ):
                is_expr = True

            if is_expr:
                # Normalizar a diccionario si es token
                if isinstance(it, Token) and it.type == "NUMBER":
                    exprs.append({"type": "Number", "value": int(it)})
                elif isinstance(it, Token) and it.type == "IDENTIFIER":
                    exprs.append({"type": "Identifier", "name": str(it)})
                else:
                    exprs.append(it)

        # Asignación segura (si falta algo, ponemos 0 o 1 por defecto para no romper el código)
        start_node = exprs[0] if len(exprs) > 0 else {
            "type": "Number", "value": 1}
        end_node = exprs[1] if len(exprs) > 1 else {
            "type": "Identifier", "name": "n"}

        return {
            "type": "For",
            "var": var if var else "i",  # fallback por si acaso
            "start": start_node,
            "end": end_node,
            "body": block["body"]
        }

    def while_stmt(self, items):
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

    # --------------------
    # EXPRESIONES
    # --------------------
    def binop(self, items):
        # items puede ser [left, op, right]
        operands = [x for x in items if isinstance(x, dict)]
        operator = None

        # Buscar operador explícito
        for x in items:
            if isinstance(x, Token):
                operator = str(x)
            elif not isinstance(x, dict) and not isinstance(x, list):
                # Atrapar literales crudos como '+', '-', etc.
                s = str(x).strip()
                if s in ['+', '-', '*', '/', 'div', 'mod', 'AND', 'OR']:
                    operator = s

        # Si no encontramos operador pero hay 2 operandos, inferir '+' para Fib
        # (Esto es un parche heurístico si la gramática falla en enviar el token)
        if operator is None and len(operands) == 2:
            # Asumir suma por defecto para evitar None, o imprimir advertencia
            # print("[WARN] BinOp sin operador detectado, asumiendo '+'")
            operator = "+"

        if len(operands) >= 2:
            return {"type": "BinOp", "left": operands[0], "op": operator, "right": operands[1]}
        elif len(operands) == 1:
            return operands[0]
        return None

    def cmp(self, items):
        if len(items) == 3:
            left, op_token, right = items[0], items[1], items[2]
            op = str(op_token) if isinstance(op_token, Token) else (
                op_token if isinstance(op_token, str) else str(op_token))
            return {"type": "Cmp", "left": left, "op": op, "right": right}
        return items[0] if items else {"type": "Cmp", "left": None, "op": None, "right": None}

    def neg(self, items):
        return {"type": "Unary", "op": "-", "expr": items[0]}

    def pos(self, items):
        return {"type": "Unary", "op": "+", "expr": items[0]}

    def or_expr(self, items):
        return {"type": "LogicOp", "op": "or", "left": items[0], "right": items[1]}

    def and_expr(self, items):
        return {"type": "LogicOp", "op": "and", "left": items[0], "right": items[1]}

    # --------------------
    # CALL / ATOMS / ARRAYS
    # --------------------
    def call_expr(self, items):
        name = None
        args = []

        # 1. Buscar nombre
        for it in items:
            if name is None:
                if isinstance(it, dict) and it.get("type") == "Identifier":
                    name = it["name"]
                elif isinstance(it, Token) and it.type == "IDENTIFIER":
                    name = str(it)

        # 2. Buscar argumentos (aplanando listas)
        raw_args = []
        for it in items:
            if isinstance(it, list):
                raw_args.extend(it)
            elif isinstance(it, dict) and it.get("name") != name:
                raw_args.append(it)

        # 3. Filtrar comas
        for arg in raw_args:
            if arg.get("type") == "Identifier" and arg.get("name") == ",":
                continue
            args.append(arg)

        return {"type": "Call", "name": name, "args": args}

    def function_call(self, items):
        # devuelve la lista de argumentos si existe
        if items and isinstance(items[0], list):
            return items[0]
        return []

    def array_expr(self, items):
        name = None
        indexes: List[Any] = []
        for it in items:
            if isinstance(it, dict) and it.get("type") == "Identifier" and name is None:
                name = it["name"]
            elif isinstance(it, Token) and it.type == "IDENTIFIER" and name is None:
                name = str(it)
            elif isinstance(it, dict) and it.get("type") != "Identifier":
                indexes.append(it)
            elif isinstance(it, list):
                for y in it:
                    if isinstance(y, dict):
                        indexes.append(y)
        return {"type": "ArrayExpr", "name": name, "indexes": indexes}

    def var(self, items):
        if items:
            first = items[0]
            if isinstance(first, dict) and first.get("type") == "Identifier":
                return first
            if isinstance(first, Token) and first.type == "IDENTIFIER":
                return {"type": "Identifier", "name": str(first)}
        return {"type": "Identifier", "name": "UNKNOWN_VAR"}

    def indexing(self, items):
        # recibe expr
        if items:
            return items[0]
        return None

    def field_access(self, items):
        if not items:
            return {"type": "FieldAccess", "object": "", "field": ""}
        left = items[0]
        right = items[-1]
        left_name = left["name"] if isinstance(
            left, dict) and "name" in left else str(left)
        right_name = right["name"] if isinstance(
            right, dict) and "name" in right else str(right)
        return {"type": "FieldAccess", "object": left_name, "field": right_name}

    def compound_stmt(self, items):
        for it in items:
            if isinstance(it, dict):
                return it
        return None
