from lark import Transformer, Token


def tree_to_ast(tree):
    return ASTBuilder().transform(tree)


class ASTBuilder(Transformer):
    # --- UTILS ---
    def _get_name(self, item):
        """Extrae el nombre limpio de un token o un diccionario Identifier"""
        if isinstance(item, dict) and item.get("type") == "Identifier":
            return item["name"]
        return str(item)

    # --- ESTRUCTURA GENERAL ---
    def start(self, items):
        classes = [x for x in items if isinstance(
            x, dict) and x.get("type") == "Class"]
        procs = [x for x in items if isinstance(
            x, dict) and x.get("type") == "Procedure"]
        return {"type": "Program", "classes": classes, "procedures": procs}

    # --- CLASES ---
    def class_decl(self, items):
        name = None
        attrs = []
        for it in items:
            if name is None:
                # Ignorar tokens de estructura, buscar el ID
                if isinstance(it, (Token, dict)):
                    s = self._get_name(it)
                    if s not in ("Clase", "{", "}"):
                        name = s
            if isinstance(it, list):
                attrs = it
        return {"type": "Class", "name": name, "attributes": attrs}

    def attribute_list(self, items):
        return [self._get_name(it) for it in items]

    def object_decl(self, items):
        return {"type": "ObjectDecl", "name": self._get_name(items[0])}

    # --- PROCEDIMIENTOS ---
    def procedure(self, items):
        name = None
        params = []
        body = []
        for it in items:
            if name is None:
                s = self._get_name(it)
                if s != "PROCEDURE":
                    name = s
            elif isinstance(it, list) and not body:
                params = it
            elif isinstance(it, dict) and it.get("type") == "Block":
                body = it["body"]
        return {"type": "Procedure", "name": name or "UNKNOWN", "params": params, "body": body}

    def param_list(self, items): return items

    def param(self, items):
        if len(items) == 2:
            return {"name": self._get_name(items[1]), "param_type": self._get_name(items[0])}
        return {"name": self._get_name(items[0]), "param_type": "any"}

    def type_spec(self, items): return self._get_name(items[0])

    # --- BLOQUES ---
    def block(self, items):
        stmts = items[0] if items else []
        return stmts if isinstance(stmts, dict) else {"type": "Block", "body": stmts}

    def stmt_list(self, items):
        stmts = []
        for x in items:
            if isinstance(x, dict):
                stmts.append(x)
            elif isinstance(x, list):
                stmts.extend(x)
        return {"type": "Block", "body": stmts}

    def statement(self, items): return items[0] if items else None

    # --- SENTENCIAS ---
    def assign_stmt(self, items):
        return {"type": "Assign", "target": items[0], "value": items[-1]}

    def if_stmt(self, items):
        return {"type": "If", "cond": items[0], "then": items[1]["body"], "else_": items[2]["body"] if len(items) > 2 else []}

    def while_stmt(self, items):
        return {"type": "While", "cond": items[0], "body": items[1]["body"]}

    def repeat_stmt(self, items):
        return {"type": "Repeat", "body": items[0]["body"], "cond": items[1]}

    def for_stmt(self, items):
        # items: [ID, ASSIGN, start, TO, end, DO, block] (Lark puede filtrar algunos)
        # Buscamos el nombre de la variable (el primer identificador)
        var_name = self._get_name(items[0])
        start = items[2]
        end = items[3]
        body = items[4]["body"]
        return {"type": "For", "var": var_name, "start": start, "end": end, "body": body}

    def return_stmt(self, items):
        return {"type": "Return", "value": items[0] if items else None}

    def call_stmt(self, items):
        # AQUÍ ESTABA EL ERROR: Usábamos str(items[0]) que podía ser un dict stringificado
        name = self._get_name(items[0])
        args = items[1] if len(items) > 1 else []
        return {"type": "Call", "name": name, "args": args}

    # --- EXPRESIONES ---
    def expr(self, items): return items[0]
    def logic_or(self, items): return self._binop_chain(items)
    def logic_and(self, items): return self._binop_chain(items)
    def comp(self, items): return self._binop_chain(items)
    def term(self, items): return self._binop_chain(items)
    def factor(self, items): return self._binop_chain(items)

    def atom(self, items): return items[0]

    def unary(self, items):
        if len(items) == 1:
            return items[0]
        return {"type": "Unary", "op": self._get_name(items[0]), "expr": items[1]}

    def floor_op(self, items): return {
        "type": "Unary", "op": "floor", "expr": items[0]}

    def ceil_op(self, items): return {
        "type": "Unary", "op": "ceil", "expr": items[0]}

    def _binop_chain(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        for i in range(1, len(items), 2):
            op = self._get_name(items[i])
            right = items[i+1]
            left = {"type": "BinOp", "left": left, "op": op, "right": right}
        return left

    def lvalue(self, items):
        parts = [self._get_name(it) for it in items]
        return {"type": "LValue", "name": ".".join(parts)}

    def array_access(self, items):
        first = items[0]
        name = self._get_name(first)
        index = items[1]
        return {"type": "ArrayAccess", "name": name, "index": index}

    def length_func(self, items):
        return {"type": "Call", "name": "length", "args": [{"type": "Identifier", "name": self._get_name(items[0])}]}

    def call_expr(self, items):
        # AQUÍ TAMBIÉN: Usar _get_name
        name = self._get_name(items[0])
        args = items[1] if len(items) > 1 else []
        return {"type": "Call", "name": name, "args": args}

    def arg_list(self, items):
        return [x for x in items if isinstance(x, dict)]

    # --- TOKENS ---
    def NUMBER(self, token): return {"type": "Number", "value": float(
        token) if '.' in token else int(token)}
    def IDENTIFIER(self, token): return {
        "type": "Identifier", "name": str(token)}

    def null_val(self, _): return {"type": "Literal", "value": "NULL"}
    def true_val(self, _): return {"type": "Literal", "value": True}
    def false_val(self, _): return {"type": "Literal", "value": False}
