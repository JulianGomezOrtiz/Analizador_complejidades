import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity

merge_sort_code = """
PROCEDURE MergeSort(A, p, r)
BEGIN
  IF p < r THEN
  BEGIN
    q <- floor((p + r) / 2);
    CALL MergeSort(A, p, q);
    CALL MergeSort(A, q + 1, r);
    CALL Merge(A, p, q, r);
  END
  ENDIF
END
"""

insertion_sort_code = """
PROCEDURE InsertionSort(A, n)
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
END
"""

def analyze(name, code):
    print(f"\n--- Analyzing {name} ---")
    try:
        tree = parse_source(code)
        ast = tree_to_ast(tree)
        context = analyze_ast_for_patterns(ast)
        result = infer_complexity(context)
        if name in result["procedures"]:
            proc = result["procedures"][name]
            comp = proc["complexity"]
            print(f"Worst: {comp['worst_case']}")
            print(f"Best:  {comp['best_case']}")
            print(f"Avg:   {comp['average_case']}")
            print("Reasoning:", proc["reasoning"])
        else:
            print(f"Procedure {name} not found in result.")
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

analyze("MergeSort", merge_sort_code)
analyze("InsertionSort", insertion_sort_code)
