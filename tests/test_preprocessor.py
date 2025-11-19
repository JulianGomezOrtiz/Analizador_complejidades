# tests/test_preprocessor.py
from analyzer.preprocessor import normalize_source


def test_remove_comments():
    src = "x := 1; ► comentario"
    out = normalize_source(src)
    assert "comentario" not in out
    assert "x" in out


def test_normalize_arrow():
    src = "x 🡨 2"
    out = normalize_source(src)
    assert ":=" in out


def test_blank_lines_collapse():
    src = "a:=1\n\n\nb:=2"
    out = normalize_source(src)
    assert out.count("\n") == 2
