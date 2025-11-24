# src/analyzer/preprocessor.py
"""
Preprocessor: limpia y normaliza el pseudocódigo de entrada para el parser.
- elimina/normaliza comentarios (► ... )
- normaliza asignación '🡨' -> ':=' (si quieres)
- asegura saltos de línea consistentes
- devuelve texto listo para Lark
"""

from typing import Tuple


def normalize_source(code: str, normalize_assign_arrow: bool = True) -> str:
    """
    Normaliza el código de entrada.

    Args:
        code: texto fuente en pseudocódigo (str).
        normalize_assign_arrow: si True, reemplaza '🡨' por ':=' para compatibilidad.

    Returns:
        Código normalizado (str).

    Nota:
        No modifica semántica; sólo limpia y prepara tokens.
    """
    if code is None:
        raise ValueError("code cannot be None")

    # 1) Normalizar saltos de línea
    text = code.replace("\r\n", "\n").replace("\r", "\n")

    # 2) Quitar comentarios '►' hasta el final de la línea
    out_lines = []
    for line in text.split("\n"):
        if "►" in line:
            line = line.split("►", 1)[0]  # Eliminar comentario
        out_lines.append(line.rstrip())

    text = "\n".join(out_lines)

    # 3) Normalizar asignación flecha a operador clásico (si se desea)
    if normalize_assign_arrow:
        text = (
            text.replace("🡨", ":=")
                .replace("←", ":=")
                .replace("→", "->")
        )

    # 4) Eliminar líneas vacías excesivas (mantener una sola línea vacía seguida)
    lines = []
    prev_blank = False
    for ln in text.split("\n"):
        if ln.strip() == "":
            if not prev_blank:
                lines.append("")
            prev_blank = True
        else:
            lines.append(ln)
            prev_blank = False

    return "\n".join(lines)
