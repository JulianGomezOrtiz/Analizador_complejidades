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

    def _get_line(self, item):
        """Intenta extraer la línea de un token o nodo"""
        if hasattr(item, "line"):
            return item.line
        if isinstance(item, dict):
            return item.get("line")
        return None

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

    def type_spec(self, items):
        # print(f"DEBUG type_spec items: {items}")
        if not items:
             return "unknown"
        return self._get_name(items[0])

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
        line = self._get_line(items[0])
        return {"type": "Assign", "target": items[0], "value": items[-1], "line": line}

    def if_stmt(self, items):
        def extract_body(node):
            if isinstance(node, dict) and node.get("type") == "Block":
                return node["body"]
            if isinstance(node, list):
                return node
            return [node]

        then_body = extract_body(items[1])
        else_body = extract_body(items[2]) if len(items) > 2 else []
        line = self._get_line(items[0]) # Line from condition
        return {"type": "If", "cond": items[0], "then": then_body, "else_": else_body, "line": line}

    def while_stmt(self, items):
        body = items[1]["body"] if isinstance(items[1], dict) and items[1].get("type") == "Block" else [items[1]]
        line = self._get_line(items[0])
        return {"type": "While", "cond": items[0], "body": body, "line": line}

    def repeat_stmt(self, items):
        body = items[0]["body"] if isinstance(items[0], dict) and items[0].get("type") == "Block" else [items[0]]
        line = self._get_line(items[1]) # Line from condition (at end) or maybe start? Lark doesn't give start token easily here without more work. 
        # Better to try to get line from body[0] if exists, or just accept it might be approximate.
        # Actually, items[0] is body. Let's try to get line from first stmt of body if possible.
        return {"type": "Repeat", "body": body, "cond": items[1], "line": None}

    def for_stmt(self, items):
        # items: [ID, ASSIGN, start, TO, end, DO, block] (Lark puede filtrar algunos)
        # Buscamos el nombre de la variable (el primer identificador)
        var_name = self._get_name(items[0])
        start = items[2]
        end = items[3]
        
        step = {"type": "Number", "value": 1}
        
        if len(items) == 6:
            # With STEP: [ID, ASSIGN, start, end, step, body]
            step = items[4]
            body_node = items[5]
        else:
            # Without STEP: [ID, ASSIGN, start, end, body]
            body_node = items[4]
            
        # Extract body list from Block node if necessary
        body = body_node["body"] if isinstance(body_node, dict) and body_node.get("type") == "Block" else body_node
        
        line = self._get_line(items[0]) # Line from var name token
        return {"type": "For", "var": var_name, "start": start, "end": end, "step": step, "body": body, "line": line}

    def return_stmt(self, items):
        line = self._get_line(items[0]) if items else None
        return {"type": "Return", "value": items[0] if items else None, "line": line}

    def call_stmt(self, items):
        # AQUÍ ESTABA EL ERROR: Usábamos str(items[0]) que podía ser un dict stringificado
        name = self._get_name(items[0])
        args = items[1] if len(items) > 1 else []
        line = self._get_line(items[0])
        return {"type": "Call", "name": name, "args": args, "line": line}

    # --- EXPRESIONES ---
    def condition(self, items): return items[0]
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
        line = self._get_line(items[0])
        return {"type": "Unary", "op": self._get_name(items[0]), "expr": items[1], "line": line}

    def floor_op(self, items): return {
        "type": "Unary", "op": "floor", "expr": items[0]}

    def ceil_op(self, items): return {
        "type": "Unary", "op": "ceil", "expr": items[0]}

    def _get_op(self, item):
        if hasattr(item, "data"): # It's a Tree
            return self._get_op(item.children[0])
        return str(item)

    def _binop_chain(self, items):
        # Caso 0: Lista vacía (Defensivo)
        if not items:
            return None

        # Caso 1: Solo un elemento (pasa directo)
        if len(items) == 1:
            return items[0]

        # Caso 2: Cadena de operaciones (left op right op right...)
        left = items[0]
        # Iteramos de 2 en 2: operador, operando derecho
        for i in range(1, len(items) - 1, 2):
            op = self._get_op(items[i])
            right = items[i+1]
            # Propagate line from left operand if available, or try to get from op token?
            # Best to keep line from the leftmost component
            line = self._get_line(left)
            left = {"type": "BinOp", "left": left, "op": op, "right": right, "line": line}

        return left

    def lvalue(self, items):
        parts = [self._get_name(it) for it in items]
        line = self._get_line(items[0]) if items else None
        return {"type": "LValue", "name": ".".join(parts), "line": line}

    def array_access(self, items):
        first = items[0]
        name = self._get_name(first)
        index = items[1]
        line = self._get_line(first)
        return {"type": "ArrayAccess", "name": name, "index": index, "line": line}

    def length_func(self, items):
        return {"type": "Call", "name": "length", "args": [{"type": "Identifier", "name": self._get_name(items[0])}]}

    def call_expr(self, items):
        # AQUÍ TAMBIÉN: Usar _get_name
        first = items[0]
        name = self._get_name(first)
        args = items[1] if len(items) > 1 else []
        line = self._get_line(first)
        
        # Convertir floor/ceil a Unary op para análisis consistente
        if name.lower() in ("floor", "ceil"):
            expr = args[0] if args else None
            return {"type": "Unary", "op": name.lower(), "expr": expr, "line": line}
            
        return {"type": "Call", "name": name, "args": args, "line": line}

    def arg_list(self, items):
        return [x for x in items if isinstance(x, dict)]

    # --- TOKENS ---
    def NUMBER(self, token): return {"type": "Number", "value": float(
        token) if '.' in token else int(token), "line": token.line}
    def IDENTIFIER(self, token): return {
        "type": "Identifier", "name": str(token), "line": token.line}

    def null_val(self, _): return {"type": "Literal", "value": "NULL"}
    def true_val(self, _): return {"type": "Literal", "value": True}
    def false_val(self, _): return {"type": "Literal", "value": False}
