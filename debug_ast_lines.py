import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.getcwd(), "src"))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast

source_code = """PROCEDURE InsertionSort(A, n)
BEGIN
  FOR i <- 2 TO n DO
  BEGIN
    key <- A[i];
    j <- i - 1;
    WHILE j > 0 and A[j] > key DO
    BEGIN
      A[j+1] <- A[j];
      j <- j - 1;
    END
    A[j+1] <- key;
  END
END"""

try:
    tree = parse_source(source_code)
    ast = tree_to_ast(tree)
    
    print("AST Structure with Lines:")
    
    def print_lines(node, depth=0):
        indent = "  " * depth
        if isinstance(node, dict):
            typ = node.get("type", "Unknown")
            line = node.get("line")
            print(f"{indent}{typ} (Line: {line})")
            
            # Recurse
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    print_lines(v, depth + 1)
        elif isinstance(node, list):
            for item in node:
                print_lines(item, depth)

    print_lines(ast)

except Exception as e:
    print(f"Error: {e}")
