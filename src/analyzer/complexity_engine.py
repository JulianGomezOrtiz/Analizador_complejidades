"""
Motor de complejidad:
Produce O, Ω, Θ de manera heurística basándose en:
- loops anidados
- recursión
- divide & conquer
- Fibonacci
"""

from typing import Dict, Any, List
import re


def _nesting_to_theta(k: int) -> str:
    if k <= 0:
        return "Theta(1)"
    if k == 1:
        return "Theta(n)"
    return f"Theta(n^{k})".replace("^", "**")


def infer_complexity(context: Dict[str, Any], proc_name=None) -> Dict[str, Any]:
    procs = context.get("procedures", {})

    if proc_name:
        targets = {proc_name: procs[proc_name]}
    else:
        targets = procs

    out = {"procedures": {}}

    for name, info in targets.items():

        loops = info.get("loops", [])
        recursions = info.get("recursions", [])
        calls = info.get("calls", [])
        max_nesting = info.get("max_nesting", 0)

        reasoning: List[str] = []

        # ============================================================================
        # RECURSIÓN
        # ============================================================================
        if recursions:
            reasoning.append(f"Detected recursive calls in '{name}'.")
            pred = _detect_recursive(info)
            pred["reasoning"].extend(reasoning)
            out["procedures"][name] = pred
            continue

        # ============================================================================
        # LOOPS
        # ============================================================================
        if loops:
            reasoning.append(
                f"Detected {len(loops)} loop(s). Maximum nesting = {max_nesting}."
            )

            uses_n = False
            for lp in loops:
                s, e = lp.get("start"), lp.get("end")
                if _mentions_symbol(s, "n") or _mentions_symbol(e, "n"):
                    uses_n = True

            theta = _nesting_to_theta(max_nesting)

            if uses_n:
                reasoning.append(
                    "Bounds reference 'n', assuming canonical loop growth.")
                big_theta = theta
                big_o = theta
                big_omega = "Theta(n)" if max_nesting == 1 else theta
            else:
                reasoning.append(
                    "Symbol 'n' not seen, using generic n^k heuristic.")
                big_theta = theta
                big_o = theta
                big_omega = "Theta(1)"

            out["procedures"][name] = {
                "big_o": big_o,
                "big_omega": big_omega,
                "big_theta": big_theta,
                "cotas_fuertes": f"c1*n^{max_nesting} <= T(n) <= c2*n^{max_nesting}",
                "recurrence": None,
                "reasoning": reasoning,
            }
            continue

        # ============================================================================
        # SIN LOOPS NI RECURSIÓN
        # ============================================================================
        reasoning.append("No loops or recursion → constant or call-dominated.")

        if calls:
            out["procedures"][name] = {
                "big_o": "Theta(1) (plus callees)",
                "big_omega": "Theta(1)",
                "big_theta": "Theta(1)",
                "cotas_fuertes": "O(1)",
                "recurrence": None,
                "reasoning": reasoning,
            }
        else:
            out["procedures"][name] = {
                "big_o": "Theta(1)",
                "big_omega": "Theta(1)",
                "big_theta": "Theta(1)",
                "cotas_fuertes": "c <= T(n) <= c",
                "recurrence": None,
                "reasoning": reasoning,
            }

    return out


# =============================================================================
# HELPERS
# =============================================================================

def _mentions_symbol(node: Any, symbol: str) -> bool:
    """Busca una variable en cualquier nodo del AST, por representación textual."""
    if node is None:
        return False

    def stringify(n):
        if isinstance(n, dict):
            if n.get("type") == "Identifier":
                return n.get("name", "")
            if n.get("type") == "Number":
                return str(n.get("value"))
            s = ""
            for v in n.values():
                if isinstance(v, list):
                    for e in v:
                        s += stringify(e) + " "
                elif isinstance(v, dict):
                    s += stringify(v) + " "
                else:
                    s += str(v) + " "
            return s
        return str(n)

    return symbol.lower() in stringify(node).lower()


def _detect_recursive(info: Dict[str, Any]) -> Dict[str, Any]:
    recs = info.get("recursions", [])
    if not recs:
        return _unknown_recursion()

    first = recs[0]
    args = first.get("args", [])

    def txt(a):
        if isinstance(a, dict) and a.get("type") == "Identifier":
            return a.get("name")
        if isinstance(a, dict) and a.get("type") == "Number":
            return str(a["value"])
        if isinstance(a, dict) and a.get("type") == "BinOp":
            return f"({txt(a['left'])}{a['op']}{txt(a['right'])})"
        return str(a)

    args_txt = [txt(a) for a in args]

    # ------ divide & conquer n/2 ------
    joined = " ".join(args_txt).lower()
    if "/2" in joined or "mid" in joined:
        return {
            "big_o": "Theta(n log n)",
            "big_omega": "Theta(n log n)",
            "big_theta": "Theta(n log n)",
            "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
            "recurrence": "T(n)=a T(n/2)+f(n)",
            "reasoning": [f"Recursive args: {args_txt}", "Detected divide & conquer."],
        }

    # ------ Fibonacci-like n-1, n-2 ------
    if re.search(r"n\s*-\s*1", joined) and re.search(r"n\s*-\s*2", joined):
        return {
            "big_o": "Theta(phi^n)",
            "big_omega": "Theta(phi^n)",
            "big_theta": "Theta(phi^n)",
            "cotas_fuertes": "T(n)=Theta(phi^n)",
            "recurrence": "T(n)=T(n-1)+T(n-2)",
            "reasoning": [f"Recursive args: {args_txt}", "Detected Fibonacci pattern."],
        }

    # ------ n-1 ------
    if re.search(r"n\s*-\s*1", joined):
        return {
            "big_o": "Theta(n)",
            "big_omega": "Theta(n)",
            "big_theta": "Theta(n)",
            "cotas_fuertes": "T(n)=Theta(n)",
            "recurrence": "T(n)=T(n-1)+O(1)",
            "reasoning": [f"Recursive args: {args_txt}", "Detected linear recursion."],
        }

    return _unknown_recursion()


def _unknown_recursion():
    return {
        "big_o": "Theta(?)",
        "big_omega": "Theta(?)",
        "big_theta": "Theta(?)",
        "cotas_fuertes": "unknown",
        "recurrence": None,
        "reasoning": ["Unknown recursion pattern."],
    }
