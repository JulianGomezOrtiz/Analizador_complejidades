from src.analyzer.diagram_generator import TraceGenerator
from src.analyzer.ast_transformer import tree_to_ast
from src.analyzer.parser import parse_source
import os
import sys

# Ajustar path para que encuentre los módulos hermanos
sys.path.append(os.path.abspath(os.path.join(
    os.path.dirname(__file__), '../../..')))


# CÓDIGO ESTRICTO (Cumple con BEGIN/END y 🡨)
CODE = """
PROCEDURE BinarySearch(A, n, x)
BEGIN
    left 🡨 1;
    right 🡨 n;
    
    WHILE left <= right DO
    BEGIN
        mid 🡨 (left + right) div 2;
        
        IF A[mid] = x THEN
        BEGIN
            RETURN mid;
        END
        ELSE
        BEGIN
            IF A[mid] < x THEN
            BEGIN
                left 🡨 mid + 1;
            END
            ELSE
            BEGIN
                right 🡨 mid - 1;
            END
        END
    END
    
    RETURN (-1);
END
"""


def test_generate_diagram():
    """
    Esta función permite que pytest ejecute el script como una prueba.
    """
    print("\n--- GENERANDO DIAGRAMA DE SEGUIMIENTO ---")
    try:
        # 1. Parsear
        tree = parse_source(CODE)
        print("✅ Parsing exitoso")

        # 2. Transformar
        ast = tree_to_ast(tree)
        print("✅ AST generado")

        # 3. Generar Diagrama
        # Asegurarse de que la carpeta exista
        output_dir = "docs/diagrams"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        gen = TraceGenerator(ast)
        gen.generate()
        print(f"✅ Diagrama guardado en {output_dir}")

    except Exception as e:
        pytest.fail(f"❌ Error generando diagrama: {e}")


if __name__ == "__main__":
    # Permite ejecutar el script directamente con python
    import pytest
    test_generate_diagram()
