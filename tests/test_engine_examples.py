import pytest
from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity


def run(src: str, proc: str):
    norm = normalize_source(src)
    tree = parse_source(norm)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name=proc)
    return out["procedures"][proc]


# --------------------------
# CORRECCIÓN 1: MergeSort con bucle de mezcla simulado
# --------------------------
MERGE = """
PROCEDURE MergeSort(A, left, right)
BEGIN
    IF left >= right THEN
    BEGIN
        RETURN 0;
    END
    mid <- (left + right) / 2;
    
    CALL MergeSort(A, left, mid);
    CALL MergeSort(A, mid+1, right);

    ► Simulamos el costo O(n) de la funcion Merge
    FOR k <- left TO right DO
    BEGIN
        x <- A[k];
    END
END
"""


def test_merge_sort_complexity():
    out = run(MERGE, "MergeSort")
    assert "n log" in out["big_o"].replace("*", " ").lower()


# --------------------------
# CORRECCIÓN 2: BinarySearch estándar
# --------------------------
BINARY = """
PROCEDURE BinarySearch(A, left, right, x)
BEGIN
    IF left > right THEN
    BEGIN
        RETURN (-1);
    END
    mid <- (left + right) / 2;
    IF A[mid] = x THEN
    BEGIN
        RETURN mid;
    END
    ELSE
    BEGIN
        IF A[mid] < x THEN
        BEGIN
            RETURN BinarySearch(A, mid+1, right, x);
        END
        ELSE
        BEGIN
            RETURN BinarySearch(A, left, mid-1, x);
        END
    END
END
"""


def test_binary_search_complexity():
    out = run(BINARY, "BinarySearch")
    assert "log" in out["big_o"].lower()


FIBO = """
PROCEDURE Fib(n)
BEGIN
    IF n <= 1 THEN
    BEGIN
        RETURN n;
    END
    RETURN Fib(n-1) + Fib(n-2);
END
"""


def test_fib_complexity():
    out = run(FIBO, "Fib")
    assert "phi" in out["big_theta"].lower() or "exp" in out["big_o"].lower()


# --------------------------
# Otros algoritmos (sin cambios, ya funcionaban)
# --------------------------
LINEAR = """
PROCEDURE LinearSearch(A, n, x)
BEGIN
    FOR i <- 1 TO n DO
    BEGIN
        IF A[i] = x THEN
        BEGIN
            RETURN i;
        END
    END
    RETURN (-1);
END
"""


def test_linear_search_complexity():
    out = run(LINEAR, "LinearSearch")
    assert "n" in out["big_o"].lower()


MATRIX = """
PROCEDURE MatrixSum(A, n)
BEGIN
    FOR i <- 1 TO n DO
    BEGIN
        FOR j <- 1 TO n DO
        BEGIN
            x <- A[i][j];
        END
    END
END
"""


def test_matrix_sum_complexity():
    out = run(MATRIX, "MatrixSum")
    assert "n**2" in out["big_theta"].replace("^", "**").lower()


TRIPLE = """
PROCEDURE TripleLoop(n)
BEGIN
    count <- 0;
    FOR i <- 1 TO n DO
    BEGIN
        FOR j <- 1 TO n DO
        BEGIN
            FOR k <- 1 TO n DO
            BEGIN
                count <- count + 1;
            END
        END
    END
END
"""


def test_triple_loop_complexity():
    out = run(TRIPLE, "TripleLoop")
    assert "n**3" in out["big_theta"].lower()


QUICKSORT = """
PROCEDURE QuickSort(A, left, right)
BEGIN
    IF left >= right THEN
    BEGIN
        RETURN 0;
    END
    CALL QuickSort(A, left, right);
END
"""


def test_quicksort_recursion_detection():
    out = run(QUICKSORT, "QuickSort")
    assert "?" in out["big_theta"] or "recursion" in " ".join(
        out["reasoning"]).lower()


LCS = """
PROCEDURE LCS(X, Y, m, n)
BEGIN
    FOR i <- 1 TO m DO
    BEGIN
        FOR j <- 1 TO n DO
        BEGIN
            x <- 1;
        END
    END
END
"""


def test_lcs_complexity():
    out = run(LCS, "LCS")
    assert "n**2" in out["big_theta"].lower() or "m" in out["big_theta"].lower()


QUEENS = """
PROCEDURE SolveQueens(board, row, n)
BEGIN
    IF row = n THEN
    BEGIN
        RETURN T;
    END
    FOR col <- 0 TO n DO
    BEGIN
        CALL SolveQueens(board, row+1, n);
    END
END
"""


def test_queens_backtracking_complexity():
    out = run(QUEENS, "SolveQueens")
    reasoning = " ".join(out["reasoning"]).lower()
    assert "?" in out["big_o"] or "recursiv" in reasoning


COUNT = """
PROCEDURE CountPairs(A, n)
BEGIN
    count <- 0;
    FOR i <- 1 TO n DO
    BEGIN
        FOR j <- i+1 TO n DO
        BEGIN
            IF A[i] < A[j] THEN
            BEGIN
                count <- count + 1;
            END
        END
    END
END
"""


def test_count_pairs_complexity():
    out = run(COUNT, "CountPairs")
    assert "n**2" in out["big_theta"].lower()
