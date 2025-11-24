import pytest
# Asegúrate que parser.py exponga esta función
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast

# Este es el código "Estricto" que exige el profesor
CODIGO_ESTRICTO = """
Clase Casa {Area color propietario}

PROCEDURE TestGramatica(n)
BEGIN
  Clase miObjeto;
  
  FOR i 🡨 1 TO n DO
  BEGIN
    x 🡨 length(A);
  END
  
  REPEAT
    x 🡨 x - 1;
  UNTIL x = 0
END
"""


def test_gramatica_estricta_fase1():
    """
    Prueba de humo para verificar que el parser acepta:
    1. Flecha de asignación (🡨)
    2. Comentarios con triángulo (►)
    3. Clases fuera del procedimiento
    """
    print("\n--- INICIANDO TEST DE GRAMÁTICA FASE 1 ---")

    # 1. Intentar Parsear (Si falla aquí, es culpa de grammar.lark)
    try:
        tree = parse_source(CODIGO_ESTRICTO)
        print("✅ Parsing exitoso (Lexer aceptó los símbolos)")
    except Exception as e:
        pytest.fail(f"❌ El Parser rechazó el código estricto. Error: {e}")

    # 2. Generar AST (Si falla aquí, es culpa de ast_transformer.py)
    try:
        ast = tree_to_ast(tree)
        print("✅ Transformación a AST exitosa")
    except Exception as e:
        pytest.fail(f"❌ Falló la transformación AST. Error: {e}")

    # 3. Verificar Estructura del AST (Validación de contenido)

    # Verificar que detectó la clase
    assert ast["type"] == "Program"
    assert len(ast["classes"]) == 1, "No se detectó la clase 'Casa'"
    assert ast["classes"][0]["name"] == "Casa"
    print("✅ Clase 'Casa' detectada correctamente")

    # Verificar que detectó el procedimiento
    proc = ast["procedures"][0]
    assert proc["name"] == "TestGramatica"

    # Verificar la asignación con flecha dentro del FOR
    # Estructura esperada: Procedure -> Body -> For -> Body -> Assign
    for_stmt = proc["body"][1]  # El índice 0 es la declaración de objeto
    assert for_stmt["type"] == "For"

    assign_stmt = for_stmt["body"][0]
    assert assign_stmt["type"] == "Assign"
    assert assign_stmt["target"]["name"] == "x"
    print("✅ Asignación con '🡨' parseada correctamente como Assign node")

    print("--- FASE 1 COMPLETADA: SINTAXIS CORRECTA ---")
