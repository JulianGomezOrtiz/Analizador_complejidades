# src/analyzer/ast_transformer.py
"""
Transformador Lark -> AST (estructura de diccionarios).
Este AST es intencionalmente simple (serializable a JSON).
"""
from lark import Transformer, Tree, Token
from typing import Any, Dict, List, Union

# Helpers para los nodos AST


def make_node(kind: str, **kwargs) -> Dict[str, Any]:
    node = {"type": kind}
    node.update(kwargs)
    return node


class PseudoTransformer(Transformer):
    """
    Transformer que convierte el parse tree de Lark en un AST serializable.
    - produce diccionarios simples
    - mantiene posiciones si están presentes
    """

    def start(self, items):
        # items: sequence of decl_or_proc
        program = {"type": "Program", "declarations": [], "procedures": []}
        for it in items:
            if it["type"] == "VarDecl":
                program["declarations"].append(it)
            elif it["type"] == "Procedure":
                program["procedures"].append(it)
            else:
                # fallback
                program.setdefault("others", []).append(it)
        return program

    ########################################################
    # Declarations and procedures
    ########################################################
    def var_decl(self, items):
        # items[0] is var_list
        return make_node("VarDecl", vars=items[0])

    def var_list(self, items):
        return items

    def var_item(self, items):
        # IDENTIFIER with optional ranges
        name = str(items[0])
        dims = []
        for el in items[1:]:
            dims.append(el)
        return {"name": name, "dims": dims}

    def routine(self, items):
        # "PROCEDURE" IDENTIFIER "(" param_list? ")" block "END" ...
        # items = [IDENTIFIER, param_list? , block]
        name = str(items[0])
        if isinstance(items[1], list):
            params = items[1]
            block = items[2]
        else:
            params = []
            block = items[1]
        return make_node("Procedure", name=name, params=params, body=block["body"])

    def param_list(self, items):
        return items

    def param(self, items):
        # either IDENTIFIER or "Clase" IDENTIFIER
        if len(items) == 1:
            return {"name": str(items[0]), "type": "var"}
        else:
            # Clase IDENTIFIER
            return {"name": str(items[1]), "type": "class"}

    def block(self, items):
        # items -> statements
        stmts = []
        for it in items:
            if it is None:
                continue
            if isinstance(it, list):
                stmts.extend(it)
            else:
                stmts.append(it)
        return {"type": "Block", "body": stmts}

    ########################################################
    # Statements
    ########################################################
    def statement(self, items):
        return items[0] if items else None

    def assign_stmt(self, items):
        lvalue, _, expr = items
        return make_node("Assign", target=lvalue, value=expr)

    def lvalue(self, items):
        # IDENTIFIER with optional accesses
        name = str(items[0])
        accesses = []
        for acc in items[1:]:
            accesses.append(acc)
        node = {"name": name}
        if accesses:
            node["accesses"] = accesses
        return make_node("LValue", **node)

    def if_stmt(self, items):
        # IF (cond) THEN block (ELSE block)? END
        cond = items[0]
        then_block = items[1]
        else_block = items[2] if len(items) > 2 else {
            "type": "Block", "body": []}
        return make_node("If", cond=cond, then=then_block["body"], else_=else_block["body"])

    def while_stmt(self, items):
        cond = items[0]
        block = items[1]
        return make_node("While", cond=cond, body=block["body"])

    def for_stmt(self, items):
        # FOR IDENT ASSIGN expr TO expr DO block END
        var = str(items[0])
        start = items[1]
        end = items[2]
        block = items[3]
        return make_node("For", var=var, start=start, end=end, body=block["body"])

    def repeat_stmt(self, items):
        # REPEAT statement* UNTIL (expr)
        # items: [stmt1, stmt2, ..., expr]
        *stmts, cond = items
        body = []
        for s in stmts:
            if s is None:
                continue
            if isinstance(s, list):
                body.extend(s)
            else:
                body.append(s)
        return make_node("Repeat", cond=cond, body=body)

    def call_stmt(self, items):
        name = str(items[0])
        args = items[1] if len(items) > 1 else []
        return make_node("Call", name=name, args=args)

    def arg_list(self, items):
        return items

    def return_stmt(self, items):
        return make_node("Return", value=items[0] if items else None)

    ########################################################
    # Expressions
    ########################################################
    def expr(self, items):
        # direct passthrough
        return items[0] if items else None

    def or_expr(self, items):
        if len(items) == 1:
            return items[0]
        return make_node("LogicOr", operands=items)

    def and_expr(self, items):
        if len(items) == 1:
            return items[0]
        return make_node("LogicAnd", operands=items)

    def not_(self, items):
        # items[0] is inner
        return make_node("Not", operand=items[0])

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        op = str(items[1].children[0]) if isinstance(
            items[1], Tree) else str(items[1])
        right = items[2]
        return make_node("BinOp", op=op, left=left, right=right)

    def arith(self, items):
        if len(items) == 1:
            return items[0]
        # binary left associative
        node = items[0]
        i = 1
        while i < len(items):
            op = items[i]
            right = items[i + 1]
            node = make_node("BinOp", op=str(op), left=node, right=right)
            i += 2
        return node

    def term(self, items):
        return self.arith(items)

    def factor(self, items):
        # items could be NUMBER, IDENTIFIER, call_expr, etc.
        return items[0]

    def call_expr(self, items):
        name = str(items[0])
        args = items[1] if len(items) > 1 else []
        return make_node("CallExpr", name=name, args=args)

    def array_access(self, items):
        name = str(items[0])
        idx = items[1]
        return make_node("ArrayAccess", array=name, index=idx)

    def field_access(self, items):
        obj = str(items[0])
        field = str(items[1])
        return make_node("FieldAccess", object=obj, field=field)

    def IDENTIFIER(self, token):
        return make_node("Identifier", name=str(token))

    def NUMBER(self, token):
        return make_node("Number", value=int(token))

    def STRING(self, token):
        s = str(token)[1:-1]
        return make_node("String", value=s)

    def ASSIGN(self, token):
        return str(token)

    def __default__(self, data, children, meta):
        # fallback for unhandled nodes: return children if single else a node
        if len(children) == 1:
            return children[0]
        return children


def tree_to_ast(tree: Tree) -> Dict:
    """
    Convierte un lark.Tree (parse result) a AST serializable.

    Args:
        tree: lark.Tree

    Returns:
        dict representando el programa (Program)
    """
    transformer = PseudoTransformer()
    ast = transformer.transform(tree)
    return ast
