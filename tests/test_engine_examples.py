# tests/test_engine_examples.py
import pytest
from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity


# --------------------------
# Helper
# --------------------------
def run(src: str, proc: str):
    norm = normalize_source(src)
    tree = parse_source(norm)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name=proc)
    return out["procedures"][proc]


# --------------------------
# 1. Linear Search — O(n)
# --------------------------
LINEAR = """
PROCEDURE LinearSearch(A, n, x)
BEGIN
    FOR i := 1 TO n DO
        IF A[i] = x THEN
            RETURN i;
        END
    END
    RETURN -1;
END
"""


def test_linear_search_complexity():
    out = run(LINEAR, "LinearSearch")
    assert "n" in out["big_o"].lower()
    assert "n" in out["big_theta"].lower()


# --------------------------
# 2. Matrix Sum — O(n²)
# --------------------------
MATRIX = """
PROCEDURE MatrixSum(A, n)
BEGIN
    FOR i := 1 TO n DO
        FOR j := 1 TO n DO
            x := A[i][j];
        END
    END
END
"""


def test_matrix_sum_complexity():
    out = run(MATRIX, "MatrixSum")
    assert "n**2" in out["big_theta"].replace("^", "**").lower()


# --------------------------
# 3. Binary Search — O(log n)
# --------------------------
BINARY = """
PROCEDURE BinarySearch(A, left, right, x)
BEGIN
    IF left > right THEN
        RETURN -1;
    END
    mid := (left + right) / 2;
    IF A[mid] = x THEN
        RETURN mid;
    ELSE
        IF A[mid] < x THEN
            RETURN BinarySearch(A, mid+1, right, x);
        ELSE
            RETURN BinarySearch(A, left, mid-1, x);
        END
    END
END
"""


def test_binary_search_complexity():
    out = run(BINARY, "BinarySearch")
    assert "log" in out["big_o"].lower() or "divide" in " ".join(
        out["reasoning"]).lower()


# --------------------------
# 4. Merge Sort — O(n log n)
# --------------------------
MERGE = """
PROCEDURE MergeSort(A, left, right)
BEGIN
    IF left >= right THEN
        RETURN;
    END

    mid := (left + right) / 2;

    CALL MergeSort(A, left, mid);
    CALL MergeSort(A, mid+1, right);
END
"""


def test_merge_sort_complexity():
    out = run(MERGE, "MergeSort")
    assert "n log" in out["big_o"].replace(
        "*", " ").lower() or "log" in out["big_o"].lower()


# --------------------------
# 5. Fibonacci Recursivo — O(φ^n)
# --------------------------
FIBO = """
PROCEDURE Fib(n)
BEGIN
    IF n <= 1 THEN
        RETURN n;
    END

    RETURN Fib(n-1) + Fib(n-2);
END
"""


def test_fib_complexity():
    out = run(FIBO, "Fib")
    assert "phi" in out["big_theta"].lower() or "exp" in out["big_o"].lower()


# --------------------------
# 6. Triple Loop — O(n³)
# --------------------------
TRIPLE = """
PROCEDURE TripleLoop(n)
BEGIN
    count := 0;
    FOR i := 1 TO n DO
        FOR j := 1 TO n DO
            FOR k := 1 TO n DO
                count := count + 1;
            END
        END
    END
END
"""


def test_triple_loop_complexity():
    out = run(TRIPLE, "TripleLoop")
    assert "n**3" in out["big_theta"].lower() or "n^3" in out["big_theta"].lower()


# --------------------------
# 7. QuickSort — n log n / n²
# --------------------------
QUICKSORT = """
PROCEDURE QuickSort(A, left, right)
BEGIN
    IF left >= right THEN
        RETURN;
    END

    CALL QuickSort(A, left, right);  ► dummy to trigger recursion detection
END
"""


def test_quicksort_recursion_detection():
    out = run(QUICKSORT, "QuickSort")
    assert "?" in out["big_theta"] or "recursion" in " ".join(
        out["reasoning"]).lower()


# --------------------------
# 8. LCS — O(n²)
# --------------------------
LCS = """
PROCEDURE LCS(X, Y, m, n)
BEGIN
    FOR i := 1 TO m DO
        FOR j := 1 TO n DO
            x := 1;
        END
    END
END
"""


def test_lcs_complexity():
    out = run(LCS, "LCS")
    assert "n**2" in out["big_theta"].lower() or "m" in out["big_theta"].lower()


# --------------------------
# 9. Backtracking — factorial
# --------------------------
QUEENS = """
PROCEDURE SolveQueens(board, row, n)
BEGIN
    IF row = n THEN
        RETURN TRUE;
    END

    FOR col := 0 TO n DO
        CALL SolveQueens(board, row+1, n);
    END
END
"""


def test_queens_backtracking_complexity():
    out = run(QUEENS, "SolveQueens")
    assert "?" in out["big_o"] or "recursion" in " ".join(
        out["reasoning"]).lower()


# --------------------------
# 10. Count Pairs — O(n²)
# --------------------------
COUNT = """
PROCEDURE CountPairs(A, n)
BEGIN
    count := 0;
    FOR i := 1 TO n DO
        FOR j := i+1 TO n DO
            IF A[i] < A[j] THEN
                count := count + 1;
            END
        END
    END
END
"""


def test_count_pairs_complexity():
    out = run(COUNT, "CountPairs")
    assert "n**2" in out["big_theta"].lower()
