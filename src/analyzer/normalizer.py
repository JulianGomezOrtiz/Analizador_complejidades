"""
normalizer.py
-------------
Normaliza el código fuente antes de enviarlo al parser.
"""

import re


def normalize_source(src: str) -> str:
    # Quitar indentación común
    lines = src.splitlines()
    # filtrar líneas vacías al inicio/fin
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    # detectar indentación mínima
    indent = None
    for ln in lines:
        stripped = ln.lstrip()
        if stripped:
            spaces = len(ln) - len(stripped)
            indent = spaces if indent is None else min(indent, spaces)

    if indent is None:
        indent = 0

    # remover indentación
    cleaned = [ln[indent:] for ln in lines]

    # unir y normalizar espacios
    out = "\n".join(cleaned)
    out = re.sub(r"[ \t]+", " ", out)          # colapsar espacios
    out = re.sub(r"\s*\n\s*", "\n", out)       # limpiar saltos
    return out.strip() + "\n"
