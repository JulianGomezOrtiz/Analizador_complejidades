# tests/test_pipeline_integration.py
import json
from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity


def test_full_pipeline():
    src = """
        PROCEDURE Demo(n)
        BEGIN
            FOR i := 1 TO n DO
                x := i;
            END
        END
        """
    # ... tus pasos de parseo ...
    src = normalize_source(src)
    tree = parse_source(src)
    ast = tree_to_ast(tree)

    # --- AQUÍ VA LA RECOMENDACIÓN ---
    print("\n--- DEBUG AST ---")
    print(json.dumps(ast, indent=2))
    print("-----------------\n")
    # --------------------------------

    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name="Demo")
