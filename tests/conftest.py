# tests/conftest.py
import pytest
from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity


def compile_pipeline(src: str, proc_name: str):
    """
    Ejecuta el pipeline completo para un procedimiento:
    preprocess → parse → ast → analyze → infer complexity
    """
    norm = normalize_source(src)
    tree = parse_source(norm)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name=proc_name)
    return ast, ctx, out
