"""
patterns.py
-----------
Analiza el AST producido por tree_to_ast y genera:
- loops
- calls
- recursions
- max_nesting (profundidad de ciclos)
Estructura que complexity_engine necesita.
"""

from typing import Dict, Any, List


def analyze_ast_for_patterns(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Entrada:
       ast = { "type": "Program", "procedures": [...] }

    Retorna:
       {
          "procedures": {
              "ProcName": {
                  "loops": [...],
                  "recursions": [...],
                  "calls": [...],
                  "max_nesting": k
              }
          },
          "global": {}
       }
    """
    result = {"procedures": {}, "global": {}}

    if ast.get("type") != "Program":
        return result

    for proc in ast.get("procedures", []):
        name = proc.get("name")
        body = proc.get("body", [])

        ctx = {
            "loops": [],
            "recursions": [],
            "calls": [],
            "max_nesting": 0,
        }

        _walk(proc, 0, name, ctx)
        result["procedures"][name] = ctx

    return result


# =============================================================================
# Recursive AST walk
# =============================================================================

def _walk(node: Any, depth: int, current_proc: str, ctx: Dict[str, Any]):
    """
    node: nodo AST (dict)
    depth: nivel de anidamiento de ciclos
    current_proc: nombre del procedimiento donde estamos
    ctx: contexto del procedimiento
    """

    if isinstance(node, list):
        for x in node:
            _walk(x, depth, current_proc, ctx)
        return

    if not isinstance(node, dict):
        return

    nodetype = node.get("type")

    # ---------------------------
    # FOR / WHILE / REPEAT loops
    # ---------------------------
    if nodetype in ("For", "While", "Repeat"):
        ctx["loops"].append({
            "type": nodetype,
            "start": node.get("start"),
            "end": node.get("end"),
        })

        new_depth = depth + 1
        ctx["max_nesting"] = max(ctx["max_nesting"], new_depth)

        # Recorrer cuerpo del loop
        _walk(node.get("body", []), new_depth, current_proc, ctx)
        return

    # ---------------------------
    # CALL
    # ---------------------------
    if nodetype == "Call":
        pname = node.get("name")
        args = node.get("args", [])

        ctx["calls"].append({
            "name": pname,
            "args": args
        })

        # Recursión directa
        if pname == current_proc:
            ctx["recursions"].append({
                "name": pname,
                "args": args
            })

    # ---------------------------
    # RETURN (puede contener expr)
    # ---------------------------
    if nodetype == "Return":
        _walk(node.get("value"), depth, current_proc, ctx)
        return

    # -------------------------------------
    # For all other nodes, walk their fields
    # -------------------------------------
    for v in node.values():
        if isinstance(v, dict) or isinstance(v, list):
            _walk(v, depth, current_proc, ctx)
