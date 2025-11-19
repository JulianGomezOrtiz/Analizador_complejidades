# src/analyzer/complexity_engine.py
"""
Motor de complejidad: recibe el contexto del analizador estático y devuelve:
- O, Omega, Theta (expresiones como strings)
- reasoning: pasos textuales
- recurrence: si se detectó
Limitaciones:
 - usa heurísticas: detecta loops anidados, recursiones comunes (binary-split, fibo),
   detecta patrones aT(n/b)+f(n) cuando es aparente.
 - es expandible; si necesitas mayor formalidad usa SymPy para manipulación simbólica.
"""
from typing import Dict, Any, List, Optional
import math
import re


def _nesting_to_theta(nesting: int) -> str:
    if nesting <= 0:
        return "Theta(1)"
    if nesting == 1:
        return "Theta(n)"
    # notation; we'll normalize later
    return f"Theta(n^{nesting})".replace("^", "**")


def infer_complexity(context: Dict[str, Any], proc_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Infers complexity for a specific procedure or for all in context.

    Args:
        context: output from analyze_ast_for_patterns
        proc_name: if None, analyze all and return mapping; else single proc.

    Returns:
        dict with keys:
          - 'procedures': { name: { big_o, big_omega, big_theta, cotas_fuertes, reasoning, recurrence } }
    """
    procs = context.get("procedures", {})
    target = {proc_name: procs[proc_name]} if proc_name else procs
    out = {"procedures": {}}

    for name, info in target.items():
        reasoning: List[str] = []
        loops = info.get("loops", [])
        recursions = info.get("recursions", [])
        calls = info.get("calls", [])
        max_nesting = info.get("max_nesting", 0)

        # Heurística 1: si hay recursiones -> analizar recursivo
        if recursions:
            reasoning.append(
                f"Detected recursive calls in procedure '{name}'.")
            # inspect typical patterns via body text heuristics
            pred = _analyze_recursive_pattern(info)
            reasoning.extend(pred["reasoning"])
            outp = {
                "big_o": pred["big_o"],
                "big_omega": pred["big_omega"],
                "big_theta": pred["big_theta"],
                "cotas_fuertes": pred["cotas_fuertes"],
                "recurrence": pred.get("recurrence"),
                "reasoning": reasoning,
            }
            out["procedures"][name] = outp
            continue

        # Heurística 2: loops-only: contar nesting y types
        if loops:
            # compute nesting by grouping loops by nesting field
            max_nest = max([l.get("nesting", 1)
                           for l in loops]) if loops else 0
            reasoning.append(
                f"Detected {len(loops)} loop(s); maximum nesting level = {max_nest}.")
            # Attempt to decide whether loop bounds are n-like
            # If any loop uses 'n' or identifier common -> assume n
            uses_n = False
            for l in loops:
                s = l.get("start")
                e = l.get("end")
                if _expr_mentions_symbol(e, "n") or _expr_mentions_symbol(s, "n"):
                    uses_n = True
            if uses_n:
                big_theta = _nesting_to_theta(max_nest)
                big_o = big_theta
                big_omega = "Theta(1)" if max_nest == 0 else "Theta(n)" if max_nest == 1 else big_theta
                reasoning.append(
                    f"Loop bounds reference 'n' → assume cost grows with n.")
            else:
                # fallback: linear for single loop otherwise n^k
                big_theta = _nesting_to_theta(max_nest)
                big_o = big_theta
                big_omega = "Theta(1)"
                reasoning.append(
                    "No obvious 'n' variable found in loop bounds — using symbolic nesting heuristic.")
            outp = {
                "big_o": big_o,
                "big_omega": big_omega,
                "big_theta": big_theta,
                "cotas_fuertes": f"c1 * n^{max_nest} <= T(n) <= c2 * n^{max_nest} for n>=n0",
                "recurrence": None,
                "reasoning": reasoning,
            }
            out["procedures"][name] = outp
            continue

        # Fallback: no loops, no recursions
        reasoning.append(
            "No loops or recursion detected; treat as constant-time or dominated by calls.")
        # if has calls, complexity depends on calls; mark as unknown but linear in calls
        if calls:
            reasoning.append(
                f"Procedure makes {len(calls)} call(s); complexity depends on callees.")
            outp = {
                "big_o": "Theta(1) (plus cost of callees)",
                "big_omega": "Theta(1)",
                "big_theta": "Theta(1)",
                "cotas_fuertes": "O(1)",
                "recurrence": None,
                "reasoning": reasoning,
            }
        else:
            outp = {
                "big_o": "Theta(1)",
                "big_omega": "Theta(1)",
                "big_theta": "Theta(1)",
                "cotas_fuertes": "c <= T(n) <= c for n>=n0",
                "recurrence": None,
                "reasoning": reasoning,
            }

        out["procedures"][name] = outp

    return out


# Helper heuristics ---------------------------------------------------------
def _expr_mentions_symbol(expr_node: Any, symbol: str) -> bool:
    """
    Heurística simple: busca el símbolo en la representación textual del nodo
    (porque el AST guarda Identifiers como nodes).
    """
    if expr_node is None:
        return False
    # convert to string representation recursively

    def repr_node(n):
        if n is None:
            return ""
        if isinstance(n, dict):
            t = n.get("type")
            if t == "Identifier":
                return n.get("name", "")
            elif t == "Number":
                return str(n.get("value"))
            else:
                s = ""
                for v in n.values():
                    if isinstance(v, dict):
                        s += repr_node(v) + " "
                    elif isinstance(v, list):
                        for e in v:
                            s += repr_node(e) + " "
                    else:
                        s += str(v) + " "
                return s
        return str(n)

    text = repr_node(expr_node).lower()
    return symbol.lower() in text


def _analyze_recursive_pattern(info: Dict[str, Any]) -> Dict[str, Any]:
    """
    Heurística para detectar patrones recursivos:
      - Binary halving: 2 calls with size n/2 -> Theta(n log n)
      - Single call T(n-1) -> Theta(n)
      - Fibonacci-like 2 calls with n-1 and n-2 -> exponential
    Nota: relies on textual inspection of 'args' in recursions.
    """
    recs = info.get("recursions", [])
    reasoning = []
    # inspect the first recursion call
    first = recs[0] if recs else None
    if not first:
        return {
            "big_o": "Theta(?)",
            "big_omega": "Theta(?)",
            "big_theta": "Theta(?)",
            "cotas_fuertes": "unknown",
            "reasoning": ["No recursive call details available."],
        }

    # attempt to parse args for typical patterns
    args = first.get("args", [])
    # canonicalize textual forms
    args_txt = []

    def to_text(a):
        if isinstance(a, dict) and a.get("type") == "Identifier":
            return a.get("name")
        if isinstance(a, dict) and a.get("type") == "BinOp":
            left = to_text(a.get("left"))
            right = to_text(a.get("right"))
            op = a.get("op")
            return f"({left}{op}{right})"
        if isinstance(a, dict) and a.get("type") == "Number":
            return str(a.get("value"))
        try:
            return str(a)
        except Exception:
            return ""
    for a in args:
        args_txt.append(to_text(a))

    reasoning.append(f"Recursive call arguments (example): {args_txt}")

    # naive detection
    # Count how many recursive calls per body by scanning 'calls' occurrences
    calls = info.get("calls", [])
    # If there are two recursive calls with arguments that contain 'n/2' or 'mid' -> divide & conquer
    text_all = " ".join(args_txt).lower()
    if any("/2" in t or "mid" in t or "div 2" in t for t in args_txt):
        reasoning.append(
            "Pattern looks like divide-and-conquer with subproblems of size n/2.")
        return {
            "big_o": "Theta(n log n)",
            "big_omega": "Theta(n log n)",
            "big_theta": "Theta(n log n)",
            "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
            "recurrence": "T(n) = a T(n/2) + f(n) (a>=2 typical)",
            "reasoning": reasoning,
        }

    # Fibonacci detection: two recursive calls with n-1 and n-2 (or similar)
    if len(recs) >= 1:
        # attempt detect T(n-1) and T(n-2) pattern by textual inspection
        joined = " ".join(args_txt)
        if re.search(r"n(\s*-\s*1)", joined) and re.search(r"n(\s*-\s*2)", joined):
            reasoning.append(
                "Pattern matches Fibonacci-like recursion (T(n)=T(n-1)+T(n-2)+O(1)).")
            return {
                "big_o": "Theta(phi^n) (exponential)",
                "big_omega": "Theta(phi^n)",
                "big_theta": "Theta(phi^n)",
                "cotas_fuertes": "T(n) ∈ Θ(φ^n) where φ=(1+√5)/2",
                "recurrence": "T(n)=T(n-1)+T(n-2)+O(1)",
                "reasoning": reasoning,
            }

    # Single recursion with n-1 -> linear
    if any(re.search(r"n\s*-\s*1", t) for t in args_txt):
        reasoning.append(
            "Pattern matches single recursive call with size n-1 -> linear complexity.")
        return {
            "big_o": "Theta(n)",
            "big_omega": "Theta(n)",
            "big_theta": "Theta(n)",
            "cotas_fuertes": "c1*n <= T(n) <= c2*n",
            "recurrence": "T(n) = T(n-1) + O(1)",
            "reasoning": reasoning,
        }

    # default: unknown recursive pattern
    reasoning.append(
        "Recursive pattern unclear — returning conservative unknown.")
    return {
        "big_o": "Theta(?)",
        "big_omega": "Theta(?)",
        "big_theta": "Theta(?)",
        "cotas_fuertes": "unknown",
        "recurrence": None,
        "reasoning": reasoning,
    }
