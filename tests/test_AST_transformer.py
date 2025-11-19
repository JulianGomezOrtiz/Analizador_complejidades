# tests/test_ast_transformer.py
from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast


def test_ast_has_program():
    src = """
    PROCEDURE X()
    BEGIN
        RETURN 1;
    END
    """
    tree = parse_source(normalize_source(src))
    ast = tree_to_ast(tree)
    assert ast["type"] == "Program"
    assert len(ast["procedures"]) == 1
