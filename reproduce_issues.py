import sys
import os

sys.path.append(os.path.join(os.getcwd(), 'src'))

from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity

# Case 1: Binary Search (Using explicit n in loop for detection)
binary_search_code = """
PROCEDURE BinarySearch(A, n, x)
BEGIN
    low <- 1;
    high <- n;
    WHILE low <= n DO
        mid <- floor((low + high) / 2);
        IF A[mid] = x THEN
            RETURN mid;
        ELSE
            IF A[mid] < x THEN
                low <- mid + 1;
            ELSE
                high <- mid - 1;
            ENDIF
        ENDIF
    END WHILE
    RETURN 0;
END
"""

# Case 2: MaxHeapify (Recursive)
max_heapify_code = """
PROCEDURE MaxHeapify(A, i, n)
BEGIN
    l <- 2 * i;
    r <- 2 * i + 1;
    largest <- i;
    IF l <= n and A[l] > A[largest] THEN
        largest <- l;
    ENDIF
    IF r <= n and r <= n and A[r] > A[largest] THEN
        largest <- r;
    ENDIF
    IF largest <> i THEN
        temp <- A[i];
        A[i] <- A[largest];
        A[largest] <- temp;
        CALL MaxHeapify(A, largest, n);
    ENDIF
END
"""

def analyze(name, code):
    print(f"\n--- Analyzing {name} ---")
    try:
        tree = parse_source(code)
        ast = tree_to_ast(tree)
        context = analyze_ast_for_patterns(ast)
        result = infer_complexity(context)
        proc = result["procedures"][name]
        comp = proc["complexity"]
        print(f"Worst: {comp['worst_case']}")
        print(f"Best:  {comp['best_case']}")
        print(f"Avg:   {comp['average_case']}")
        print("Reasoning:", proc["reasoning"])
    except Exception as e:
        print(f"ERROR: {e}")

analyze("BinarySearch", binary_search_code)
analyze("MaxHeapify", max_heapify_code)
