import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity

code = """
PROCEDURE LinearSearch(A, x)
BEGIN
    i <- 0;
    n <- length(A);
    WHILE i < n DO
        IF A[i] = x THEN
            RETURN i;
        ENDIF
        i <- i + 1;
    END WHILE
    RETURN -1;
END
"""

print("Parsing code...")
tree = parse_source(code)
print("Transforming to AST...")
ast = tree_to_ast(tree)
print("Analyzing AST...")
context = analyze_ast_for_patterns(ast)
print("Inferring Complexity...")
result = infer_complexity(context)

proc = result["procedures"]["LinearSearch"]
comp = proc["complexity"]

print("\n--- RESULTS ---")
print(f"Worst Case (Big-O): {comp['worst_case']}")
print(f"Best Case (Big-Omega): {comp['best_case']}")
print(f"Average Case (Big-Theta): {comp['average_case']}")

print("\n--- REASONING ---")
for line in proc["reasoning"]:
    print(line)

# Validation
if "Theta(n)" in comp['worst_case'].replace("O", "Theta") and "Omega(1)" in comp['best_case']:
    print("\n✅ SUCCESS: Detected O(n) worst case and Omega(1) best case.")
else:
    print("\n❌ FAILURE: Complexity mismatch.")
