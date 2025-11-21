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
        # items: sequence of routines
        program = {"type": "Program", "declarations": [], "procedures": []}
        for it in items:
            if isinstance(it, dict) and it.get("type") == "VarDecl":
                program["declarations"].append(it)
            elif isinstance(it, dict) and it.get("type") == "Procedure":
                program["procedures"].append(it)
            else:
                program.setdefault("others", []).append(it)
        return program

    ########################################################
    # Declarations and procedures
    ########################################################
    def var_decl(self, items):
        return make_node("VarDecl", vars=items[0])

    def var_list(self, items):
        return items

    def var_item(self, items):
        name = str(items[0])
        dims = []
        for el in items[1:]:
            dims.append(el)
        return {"name": name, "dims": dims}

    def routine(self, items):
        # PROCEDURE IDENTIFIER "(" param_list? ")" block
        name = str(items[0])
        if len(items) == 3:
            params = items[1] if isinstance(items[1], list) else []
            block = items[2]
        else:
            # no params
            params = []
            block = items[1]
        return make_node("Procedure", name=name, params=params, body=block["body"])

    def param_list(self, items):
        return items

    def param(self, items):
        return {"name": str(items[0]), "type": "var"}

    def block(self, items):
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
        name = str(items[0])
        accesses = []
        for acc in items[1:]:
            accesses.append(acc)
        node = {"name": name}
        if accesses:
            node["accesses"] = accesses
        return make_node("LValue", **node)

    def if_stmt(self, items):
        cond = items[0]
        then_block = {"body": items[1]} if isinstance(
            items[1], list) else items[1]
        else_block = {"body": items[2]} if len(
            items) > 2 else {"type": "Block", "body": []}
        return make_node("If", cond=cond, then=then_block["body"], else_=else_block.get("body", []))

    def while_stmt(self, items):
        cond = items[0]
        block = items[1]
        return make_node("While", cond=cond, body=block["body"])

    def for_stmt(self, items):
        # FOR IDENT ASSIGN expr TO expr DO stmt_list END
        var = str(items[0])
        start = items[1]
        end = items[2]
        block = items[3]
        return make_node("For", var=var, start=start, end=end, body=block)

    def repeat_stmt(self, items):
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
        return items[0] if items else None

    def or_expr(self, items):
        if len(items) == 1:
            return items[0]
        return make_node("LogicOr", operands=items)

    def and_expr(self, items):
        if len(items) == 1:
            return items[0]
        return make_node("LogicAnd", operands=items)

    def unary(self, items):
        op = str(items[0])
        val = items[1] if len(items) > 1 else items[0]
        # if transformer passes ("+"|"-") and factor, items may be [ '-', <node> ] or if Lark grouped differently
        if isinstance(val, list):
            # defensive
            val = val[0]
        return make_node("UnaryOp", op=op, operand=val)

    def comparison(self, items):
        if len(items) == 1:
            return items[0]
        left = items[0]
        op_token = items[1]
        right = items[2]
        op = str(op_token) if not isinstance(
            op_token, Tree) else str(op_token.children[0])
        return make_node("BinOp", op=op, left=left, right=right)

    def arith(self, items):
        if len(items) == 1:
            return items[0]
        node = items[0]
        i = 1
        while i < len(items):
            op = items[i]
            right = items[i + 1]
            node = make_node("BinOp", op=str(op), left=node, right=right)
            i += 2
        return node

    def id_with_calls_or_indexes(self, items):
        # first is IDENTIFIER, followed by zero or more function_call or indexing
        name = str(items[0])
        rest = items[1:]
        node = make_node("Identifier", name=name)
        # process rest: function_call returns list of args, indexing returns index nodes
        # We'll fold them: if first rest is function_call -> CallExpr, then indexes become access of call result
        current = node
        for r in rest:
            if isinstance(r, list):
                # function_call returns list (arg_list) or empty list
                current = make_node("CallExpr", name=name if current.get(
                    "type") == "Identifier" else None, args=r)
            else:
                # indexing -> should be a node like index expression; wrap into ArrayAccess
                current = make_node("ArrayAccess", array=(
                    current.get("name") or current), index=r)
        return current

    def function_call(self, items):
        # returns arg list (possibly empty)
        return items[0] if items else []

    def indexing(self, items):
        # items: expr ; in grammar indexing can be repeated, but transformer will call it repeatedly
        return items[0]

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
