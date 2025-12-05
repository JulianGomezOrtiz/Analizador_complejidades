import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.getcwd(), "src"))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import LineCostAnalyzer

source_code = """PROCEDURE MergeSort(A, p, r)
BEGIN
  IF p < r THEN
  BEGIN
    q <- floor((p + r) / 2);
    MergeSort(A, p, q);
    MergeSort(A, q + 1, r);
    Merge(A, p, q, r);
  END
END"""

try:
    tree = parse_source(source_code)
    ast = tree_to_ast(tree)
    
    print("AST Structure for Call nodes:")
    
    def print_calls(node, depth=0):
        if isinstance(node, dict):
            typ = node.get("type")
            if typ == "Call":
                print(f"  Call: {node.get('name')} (Line: {node.get('line')})")
            
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    print_calls(v, depth + 1)
        elif isinstance(node, list):
            for item in node:
                print_calls(item, depth)

    print_calls(ast)

    print("\nLine Cost Analysis:")
    # Extract proc name from AST
    proc_name = ast["procedures"][0]["name"]
    print(f"Procedure Name: {proc_name}")
    
    analyzer = LineCostAnalyzer(proc_name)
    analyzer.visit(ast["procedures"][0]["body"])
    
    for line, cost in analyzer.line_costs.items():
        print(f"Line {line}: {cost}")

except Exception as e:
    print(f"Error: {e}")
