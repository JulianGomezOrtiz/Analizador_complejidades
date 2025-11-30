
import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.getcwd(), "src"))

from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity
from analyzer.ast_transformer import tree_to_ast
from lark import Lark

grammar = r"""
    ?start: (procedure | class_decl)*

    class_decl: "CLASS" "{" attribute_list "}"
    attribute_list: attribute*
    attribute: ID

    procedure: "PROCEDURE" ID "(" param_list ")" block
    param_list: (param ("," param)*)?
    param: ID ":" type_spec | ID
    type_spec: "INTEGER" | "ARRAY" | "STRING"

    block: "BEGIN" stmt_list "END"
    stmt_list: statement*

    statement: assign_stmt ";"
             | if_stmt
             | while_stmt
             | repeat_stmt
             | for_stmt
             | call_stmt ";"
             | return_stmt ";"

    assign_stmt: lvalue ASSIGN expr
    if_stmt: "IF" expr "THEN" block ("ELSE" block)? ("ENDIF" | "END" "IF")?
    while_stmt: "WHILE" expr "DO" block
    repeat_stmt: "REPEAT" block "UNTIL" expr
    for_stmt: "FOR" ID ASSIGN expr "TO" expr ("STEP" expr)? "DO" block
    call_stmt: "CALL" ID "(" arg_list ")"
    return_stmt: "RETURN" expr

    expr: logic_or
    logic_or: logic_and ("or" logic_and)*
    logic_and: comp ("and" comp)*
    comp: term (cmp_op term)*
    term: factor (add_op factor)*
    factor: unary (mul_op unary)*
    unary: ("-" | "not" | "floor" | "ceil") unary | atom
    atom: ID | NUMBER | STRING | lvalue | call_expr | "(" expr ")"

    !cmp_op: "<" | ">" | "<=" | ">=" | "=" | "<>" | "!="
    !add_op: "+" | "-"
    !mul_op: "*" | "/" | "div" | "mod"

    lvalue: ID ("[" expr "]")*
    call_expr: ID "(" arg_list ")"
    arg_list: (expr ("," expr)*)?

    ID: /[a-zA-Z_][a-zA-Z0-9_]*/
    NUMBER: /\d+/
    STRING: /"[^"]*"/
    ASSIGN: "<-"

    %import common.WS
    %ignore WS
"""

quicksort_code = """
PROCEDURE QuickSort(A, p, r)
BEGIN
    IF p < r THEN
    BEGIN
        q <- Partition(A, p, r);
        CALL QuickSort(A, p, q - 1);
        CALL QuickSort(A, q + 1, r);
    END
    ENDIF
END
"""

def test_quicksort():
    parser = Lark(grammar, start="start")
    tree = parser.parse(quicksort_code)
    ast = tree_to_ast(tree)
    if ast.get("type") == "Procedure":
        ast = {"type": "Program", "procedures": [ast], "classes": []}
    
    # Run Static Analysis
    context = analyze_ast_for_patterns(ast)
    
    # Run Complexity Inference
    result = infer_complexity(context, "QuickSort")
    
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_quicksort()
