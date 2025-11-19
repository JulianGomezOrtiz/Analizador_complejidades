# src/analyzer/example_usage.py
"""
Ejemplo rápido de uso:
- Normaliza
- Parsea
- Transforma a AST
- Analiza patrones
- Infiera complejidad
- Formatea reporte
"""
from .preprocessor import normalize_source
from .parser import parse_source
from .ast_transformer import tree_to_ast
from .static_analyzer import analyze_ast_for_patterns
from .complexity_engine import infer_complexity
from .reporter import format_analysis_json, format_analysis_text


SAMPLE = """
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


def run_sample():
    src = normalize_source(SAMPLE)
    tree = parse_source(src)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    engine_out = infer_complexity(ctx, proc_name="LinearSearch")
    report_json = format_analysis_json(ast, engine_out)
    report_text = format_analysis_text(engine_out)
    print(report_text)
    return report_json


if __name__ == "__main__":
    run_sample()
