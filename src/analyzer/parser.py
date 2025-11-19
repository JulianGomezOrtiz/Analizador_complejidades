# src/analyzer/parser.py
"""
Parser usando Lark. Expone parse_source(code: str) -> lark.Tree
Incluye la gramática base (ampliable).
"""
from lark import Lark, UnexpectedInput, Tree
from typing import Tuple
import pkgutil
import os

GRAMMAR = r"""
// grammar.lark - minimal / extendable grammar for the project's pseudocode
%import common.CNAME -> IDENTIFIER
%import common.INT -> NUMBER
%import common.WS
%import common.NEWLINE
%ignore WS

COMMENT: "►" /[^\n]/*      -> COMMENT
%ignore COMMENT

start: (decl_or_proc)*

decl_or_proc: routine | var_decl

var_decl: "VAR" var_list ";"
var_list: var_item ("," var_item)*
var_item: IDENTIFIER ("[" range "]")*

range: NUMBER (".." NUMBER)?
     | IDENTIFIER

routine: "PROCEDURE" IDENTIFIER "(" param_list? ")" block "END" ("PROCEDURE")?
param_list: param ("," param)*
param: IDENTIFIER ("[" range "]")? | "Clase" IDENTIFIER

block: "BEGIN" statement* "END"

statement: assign_stmt ";"
         | if_stmt
         | while_stmt
         | for_stmt
         | repeat_stmt
         | call_stmt ";"
         | return_stmt ";"
         | ";"

assign_stmt: lvalue ASSIGN expr
lvalue: IDENTIFIER ("." IDENTIFIER | "[" expr "]")*

if_stmt: "IF" "(" expr ")" "THEN" block ("ELSE" block)? "END"
while_stmt: "WHILE" "(" expr ")" "DO" block "END"
for_stmt: "FOR" IDENTIFIER ASSIGN expr "TO" expr "DO" block "END"
repeat_stmt: "REPEAT" statement* "UNTIL" "(" expr ")" ";"

call_stmt: "CALL" IDENTIFIER "(" arg_list? ")"
arg_list: expr ("," expr)*

return_stmt: "RETURN" expr?

?expr: or_expr
?or_expr: and_expr ("or" and_expr)*
?and_expr: not_expr ("and" not_expr)*
?not_expr: "not" not_expr -> not
         | comparison
?comparison: arith ((">"|"<"|"<="|">="|"="|"<>"|"!=") arith)?
?arith: term (("+"|"-") term)*
?term: factor (("*"|"/"|"div"|"mod") factor)*
?factor: "-" factor
       | "+" factor
       | call_expr
       | "(" expr ")"
       | "NULL"      -> null
       | IDENTIFIER
       | NUMBER
       | STRING
       | IDENTIFIER "[" expr "]" -> array_access
       | IDENTIFIER "." IDENTIFIER -> field_access

call_expr: IDENTIFIER "(" arg_list? ")"

ASSIGN: "🡨" | ":="

STRING: /"([^"\\]|\\.)*"/
%ignore /[ \t\r\n]+/
"""

# Create parser instance once (costly to build)
LARK_PARSER = Lark(GRAMMAR, start="start", parser="lalr",
                   propagate_positions=True)


def parse_source(code: str) -> Tree:
    """
    Parsea el pseudocódigo en un lark.Tree.

    Lanza:
      - UnexpectedInput en caso de error de parseo
    """
    if not isinstance(code, str):
        raise ValueError("code must be a string")

    try:
        tree = LARK_PARSER.parse(code)
        return tree
    except UnexpectedInput as e:
        # re-lanzar para el llamador; incluye contexto
        raise e
