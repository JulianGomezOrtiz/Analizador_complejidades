from src.analyzer.parser import parse_source
from src.analyzer.ast_transformer import tree_to_ast

code = """
PROCEDURE EightQueens()
BEGIN
    int N;
    N <- 8;
    int board[N+1];
    int totalSolutions;
    totalSolutions <- SolveQueens(board, 1, N);
    RETURN totalSolutions;
END
"""

try:
    print("Parsing...")
    tree = parse_source(code)
    print("Transforming...")
    ast = tree_to_ast(tree)
    print("Success!")
    print(ast)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
