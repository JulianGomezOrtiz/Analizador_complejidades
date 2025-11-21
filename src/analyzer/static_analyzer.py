"""
Analizador estático que recorre el AST y extrae:
- loops (anidados, límites simbólicos)
- recursiones (llamadas a la misma procedure)
- llamadas (CALL)
- variables usadas
Devuelve un "context" consumible por complexity_engine.
"""

from typing import Dict, Any, List, Tuple, Set


def analyze_ast_for_patterns(ast: Dict[str, Any]) -> Dict[str, Any]:
    result = {"procedures": {}, "global": {}}

    procedures = ast.get("procedures", [])

    for proc in procedures:
        name = proc.get("name")

        ctx = {
            "loops": [],
            "recursions": [],
            "calls": [],
            "max_nesting": 0,
            "variables": set(),
            "annotations": {},
        }

        body = proc.get("body", [])

        # --- Recursive walk ----------------------------------------------------
        def walk(stmts, nesting=0):
            ctx["max_nesting"] = max(ctx["max_nesting"], nesting)

            for s in stmts:
                if not s:
                    continue

                stype = s.get("type")

                # ----------- FOR -------------------
                if stype == "For":
                    ctx["loops"].append(
                        {
                            "type": "For",
                            "var": s.get("var"),
                            "start": s.get("start"),
                            "end": s.get("end"),
                            "body": s.get("body", []),
                            "nesting": nesting + 1,
                        }
                    )
                    walk(s.get("body", []), nesting + 1)

                # ----------- WHILE ------------------
                elif stype == "While":
                    ctx["loops"].append(
                        {
                            "type": "While",
                            "cond": s.get("cond"),
                            "body": s.get("body", []),
                            "nesting": nesting + 1,
                        }
                    )
                    walk(s.get("body", []), nesting + 1)

                # ----------- REPEAT -----------------
                elif stype == "Repeat":
                    ctx["loops"].append(
                        {
                            "type": "Repeat",
                            "cond": s.get("cond"),
                            "body": s.get("body", []),
                            "nesting": nesting + 1,
                        }
                    )
                    walk(s.get("body", []), nesting + 1)

                # ----------- IF ---------------------
                elif stype == "If":
                    walk(s.get("then", []), nesting + 1)
                    walk(s.get("else_", []), nesting + 1)

                # ----------- CALL --------------------
                elif stype == "Call":
                    cname = s.get("name")
                    ctx["calls"].append(
                        {"name": cname, "args": s.get("args", [])}
                    )
                    if cname == name:
                        ctx["recursions"].append(
                            {"call": s, "args": s.get("args", [])}
                        )

                # ----------- ASSIGN ------------------
                elif stype == "Assign":
                    tgt = s.get("target", {})
                    if tgt.get("type") == "LValue":
                        ctx["variables"].add(tgt.get("name"))

                # fallback for container nodes
                elif isinstance(s, dict):
                    for v in s.values():
                        if isinstance(v, list):
                            walk(v, nesting)

        walk(body, nesting=0)

        ctx["annotations"]["num_loops"] = len(ctx["loops"])
        ctx["annotations"]["num_calls"] = len(ctx["calls"])
        ctx["variables"] = sorted(list(ctx["variables"]))

        result["procedures"][name] = ctx

    return result
