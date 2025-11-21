# parser.py - Cargador del parser usando grammar.lark
from lark import Lark, Transformer, v_args
import pkgutil
import os

# Si tu proyecto ya carga grammar desde archivo, ajusta la ruta aquí:
THIS_DIR = os.path.dirname(__file__)
GRAMMAR_PATH = os.path.join(THIS_DIR, "grammar.lark")

# Construye el parser LALR con la gramática corregida
with open(GRAMMAR_PATH, "r", encoding="utf-8") as f:
    GRAMMAR = f.read()

LARK_PARSER = Lark(
    GRAMMAR,
    start="start",
    parser="lalr",
    propagate_positions=True,
    maybe_placeholders=False
)


def parse_source(source: str):
    """
    Parsea el código fuente normalizado y devuelve el árbol de Lark.
    """
    return LARK_PARSER.parse(source)
