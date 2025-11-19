# src/analyzer/static_analyzer.py
"""
Analizador estático que recorre el AST y extrae:
- loops (anidados, límites simbólicos)
- recursions (llamadas a la misma procedure)
- llamadas (CALL)
- variables y sus tipos/uso (simple heurística)
Devuelve un "context" consumible por complexity_engine.
"""
from typing import Dict, Any, List, Tuple, Set
from collections import defaultdict


def analyze_ast_for_patterns(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extrae información estructurada del AST.

    Devuelve:
      {
        "procedures": {
            proc_name: {
                "loops": [ { "type":"For"/"While"/"Repeat", "var":..., "start":..., "end":..., "body":..., "nesting_level":k } ],
                "recursions": [ { "call_node":..., "args":... } ],
                "calls": [ { "name":..., "args":... } ],
                "max_nesting": int,
                "variables": set(),
                "annotations": {...}
            }
        },
        "global": {...}
      }
    """
    result = {"procedures": {}, "global": {}}

    procs = ast.get("procedures", [])
    for proc in procs:
        name = proc.get("name")
        ctx = {
            "loops": [],
            "recursions": [],
            "calls": [],
            "max_nesting": 0,
            "variables": set(),
            "annotations": {},
        }

        # walk procedure body
        def walk_statements(stmts, nesting=0):
            ctx["max_nesting"] = max(ctx["max_nesting"], nesting)
            for s in stmts:
                if s is None:
                    continue
                stype = s.get("type")
                if stype == "For":
                    ctx["loops"].append(
                        {
                            "type": "For",
                            "var": s.get("var"),
                            "start": s.get("start"),
                            "end": s.get("end"),
                            "body": s.get("body"),
                            "nesting": nesting + 1,
                        }
                    )
                    walk_statements(s.get("body", []), nesting + 1)
                elif stype == "While":
                    ctx["loops"].append(
                        {
                            "type": "While",
                            "cond": s.get("cond"),
                            "body": s.get("body"),
                            "nesting": nesting + 1,
                        }
                    )
                    walk_statements(s.get("body", []), nesting + 1)
                elif stype == "Repeat":
                    ctx["loops"].append(
                        {
                            "type": "Repeat",
                            "cond": s.get("cond"),
                            "body": s.get("body"),
                            "nesting": nesting + 1,
                        }
                    )
                    walk_statements(s.get("body", []), nesting + 1)
                elif stype == "If":
                    # then
                    walk_statements(s.get("then", []), nesting + 1)
                    walk_statements(s.get("else_", []), nesting + 1)
                elif stype == "Call":
                    cname = s.get("name")
                    ctx["calls"].append(
                        {"name": cname, "args": s.get("args", [])})
                    # detect recursion: call to same proc name
                    if cname == name:
                        ctx["recursions"].append(
                            {"call": s, "args": s.get("args", [])})
                elif stype == "Assign":
                    # collect variables used
                    tgt = s.get("target", {})
                    if tgt.get("type") == "LValue":
                        ctx["variables"].add(tgt.get("name"))
                elif stype == "Return":
                    pass
                else:
                    # fallback: if body field exists, try to walk it
                    if isinstance(s, dict):
                        for v in s.values():
                            if isinstance(v, list):
                                walk_statements(v, nesting)

        body = proc.get("body", [])
        walk_statements(body, nesting=0)

        # simple annotations: detect nested loops depth
        ctx["annotations"]["num_loops"] = len(ctx["loops"])
        ctx["annotations"]["num_calls"] = len(ctx["calls"])
        ctx["variables"] = sorted(list(ctx["variables"]))
        result["procedures"][name] = ctx

    return result
