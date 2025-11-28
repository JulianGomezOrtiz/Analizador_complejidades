import sys
import os

# Configurar path para importar módulos del proyecto
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '../../'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from analyzer.diagram_generator import TraceGenerator
from analyzer.ast_transformer import tree_to_ast
from analyzer.parser import parse_source


# ==========================================
# PORTFOLIO DE ALGORITMOS (Sintaxis Estricta)
# ==========================================
ALGORITHMS = {
    "1_LinearSearch": """
        PROCEDURE LinearSearch(A, n, x)
        BEGIN
            FOR i 🡨 1 TO n DO
            BEGIN
                IF A[i] = x THEN
                BEGIN
                    RETURN i;
                END
            END
            RETURN (-1);
        END
    """,
    "2_MatrixSum": """
        PROCEDURE MatrixSum(A, n)
        BEGIN
            total 🡨 0;
            FOR i 🡨 1 TO n DO
            BEGIN
                FOR j 🡨 1 TO n DO
                BEGIN
                    total 🡨 total + A[i][j];
                END
            END
            RETURN total;
        END
    """,
    "3_BinarySearch": """
        PROCEDURE BinarySearch(A, left, right, x)
        BEGIN
            IF left > right THEN
            BEGIN
                RETURN (-1);
            END
            mid 🡨 (left + right) div 2;
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
    """,
    "4_MergeSort": """
        PROCEDURE MergeSort(A, left, right)
        BEGIN
            IF left >= right THEN
            BEGIN
                RETURN 0;
            END
            mid 🡨 (left + right) div 2;
            CALL MergeSort(A, left, mid);
            CALL MergeSort(A, mid+1, right);
            
            ► Simulación del proceso de mezcla (Merge)
            FOR k 🡨 left TO right DO
            BEGIN
                temp 🡨 A[k];
            END
        END
    """,
    "5_Fibonacci": """
        PROCEDURE Fib(n)
        BEGIN
            IF n <= 1 THEN
            BEGIN
                RETURN n;
            END
            RETURN Fib(n-1) + Fib(n-2);
        END
    """,
    "6_TripleLoop": """
        PROCEDURE TripleLoop(n)
        BEGIN
            count 🡨 0;
            FOR i 🡨 1 TO n DO
            BEGIN
                FOR j 🡨 1 TO n DO
                BEGIN
                    FOR k 🡨 1 TO n DO
                    BEGIN
                        count 🡨 count + 1;
                    END
                END
            END
            RETURN count;
        END
    """,
    "7_QuickSort": """
        PROCEDURE QuickSort(A, low, high)
        BEGIN
            IF low < high THEN
            BEGIN
                pi 🡨 Partition(A, low, high);
                CALL QuickSort(A, low, pi - 1);
                CALL QuickSort(A, pi + 1, high);
            END
        END
    """,
    "8_LCS_Dynamic": """
        PROCEDURE LCS(X, Y, m, n)
        BEGIN
            FOR i 🡨 0 TO m DO
            BEGIN
                FOR j 🡨 0 TO n DO
                BEGIN
                    IF i=0 or j=0 THEN
                    BEGIN
                        L[i][j] 🡨 0;
                    END
                    ELSE
                    BEGIN
                        IF X[i] = Y[j] THEN
                        BEGIN
                            L[i][j] 🡨 1 + L[i-1][j-1];
                        END
                        ELSE
                        BEGIN
                            L[i][j] 🡨 max(L[i-1][j], L[i][j-1]);
                        END
                    END
                END
            END
            RETURN L[m][n];
        END
    """,
    "9_NQueens": """
        PROCEDURE SolveQueens(board, col, n)
        BEGIN
            IF col >= n THEN
            BEGIN
                RETURN T;
            END
            
            FOR i 🡨 0 TO n DO
            BEGIN
                IF IsSafe(board, i, col) THEN
                BEGIN
                    board[i][col] 🡨 1;
                    IF SolveQueens(board, col + 1, n) THEN
                    BEGIN
                        RETURN T;
                    END
                    board[i][col] 🡨 0;
                END
            END
            RETURN F;
        END
    """,
    "10_CountPairs": """
        PROCEDURE CountPairs(A, n)
        BEGIN
            count 🡨 0;
            FOR i 🡨 0 TO n-1 DO
            BEGIN
                FOR j 🡨 i+1 TO n DO
                BEGIN
                    IF A[i] + A[j] = 10 THEN
                    BEGIN
                        count 🡨 count + 1;
                    END
                END
            END
            RETURN count;
        END
    """
}


def main():
    print("\n🚀 INICIANDO GENERACIÓN MASIVA DE DIAGRAMAS CFG\n")

    output_dir = os.path.abspath(os.path.join(src_path, '../docs/diagrams'))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📂 Directorio creado: {output_dir}")

    success_count = 0

    for name, code in ALGORITHMS.items():
        try:
            print(f"🎨 Generando: {name}...", end=" ")
            tree = parse_source(code)
            ast = tree_to_ast(tree)

            # Instanciar generador
            gen = TraceGenerator(ast)
            # Sobrescribimos el nombre en el AST para que el archivo tenga el nombre de la clave (ej: 1_LinearSearch)
            ast["procedures"][0]["name"] = name

            gen.generate()
            print("✅ Hecho.")
            success_count += 1
        except Exception as e:
            print(f"❌ Error: {e}")

    print(
        f"\n✨ PROCESO COMPLETADO: {success_count}/{len(ALGORITHMS)} diagramas generados.")
    print(f"📂 Ubicación: {output_dir}")


if __name__ == "__main__":
    main()
