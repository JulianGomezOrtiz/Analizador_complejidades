import sys
import os

# Adjust path to import src
sys.path.append(os.path.join(os.getcwd(), "src"))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast

# Minimal case: Just one call
source_code = """PROCEDURE Test(n)
BEGIN
  Test(n-1);
END"""

try:
    print("Parsing minimal source...")
    tree = parse_source(source_code)
    print("Parse successful!")
    ast = tree_to_ast(tree)
    print("AST generated.")
    print(ast)

except Exception as e:
    print(f"Error: {e}")
