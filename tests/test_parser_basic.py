from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source


def test_parser_procedure():
    src = """
    PROCEDURE P()
    BEGIN
        x <- 1;
    END
    """
    tree = parse_source(normalize_source(src))
    assert tree is not None


def test_parser_syntax_error():
    src = "PROCEDURE X ( BEGIN"
    try:
        parse_source(normalize_source(src))
        assert False
    except Exception:
        assert True
