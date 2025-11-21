# tests/conftest.py

from analyzer.complexity_engine import infer_complexity
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.ast_transformer import tree_to_ast
from analyzer.parser import parse_source
from analyzer.preprocessor import normalize_source
import os
import sys

# --------------------------------------------------------
# 1. Agregar la ruta src al PYTHONPATH ANTES de importar
# --------------------------------------------------------

# Ruta absoluta a la raíz del proyecto (carpeta que contiene src/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Ruta absoluta a /src
SRC_PATH = os.path.join(PROJECT_ROOT, "src")

# Insertar al inicio del PYTHONPATH
sys.path.insert(0, SRC_PATH)

print("DEBUG -- SRC_PATH agregado:", SRC_PATH)
print("DEBUG -- sys.path ahora contiene:")
for p in sys.path:
    print("   ", p)

# --------------------------------------------------------
# 2. AHORA sí se importan los módulos
# --------------------------------------------------------


def compile_pipeline(src: str, proc_name: str):
    """Pipeline completo"""
    norm = normalize_source(src)
    tree = parse_source(norm)
    ast = tree_to_ast(tree)
    ctx = analyze_ast_for_patterns(ast)
    out = infer_complexity(ctx, proc_name)
    return ast, ctx, out
