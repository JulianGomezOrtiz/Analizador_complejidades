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
            FOR i 🡨 1 TO n DO
            BEGIN
                x 🡨 i;
            END
        END
        """
    src = normalize_source(src)
    tree = parse_source(src)
    ast = tree_to_ast(tree)

    print("\n--- DEBUG AST ---")
    print(json.dumps(ast, indent=2))
    print("-----------------\n")

    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name="Demo")

    res = out["procedures"]["Demo"]
    # Verificar que detecta complejidad lineal
    assert "n" in res["big_o"].lower(
    ) or "theta(n)" in res["big_theta"].lower()


def test_full_pipeline():
    src = """
        PROCEDURE Demo(n)
        BEGIN
            FOR i <- 1 TO n DO
            BEGIN
                x <- i;
            END
        END
        """
    src = normalize_source(src)
    tree = parse_source(src)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name="Demo")
    res = out["procedures"]["Demo"]
    assert "n" in res["big_o"].lower(
    ) or "theta(n)" in res["big_theta"].lower()
