"""
Motor de complejidad:
Produce O, Ω, Θ de manera heurística basándose en:
- loops anidados
- recursión (distingue logarítmica vs lineal vs exponencial)
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
    targets = {proc_name: procs[proc_name]} if proc_name else procs
    out = {"procedures": {}}

    for name, info in targets.items():
        loops = info.get("loops", [])
        recursions = info.get("recursions", [])
        calls = info.get("calls", [])

        # Ajuste de anidamiento
        raw_nesting = info.get("max_nesting", 0)
        loop_count = len(loops)
        max_nesting = min(raw_nesting, loop_count) if loop_count > 0 else 0
        if raw_nesting > 0 and loop_count >= raw_nesting:
            max_nesting = raw_nesting

        reasoning: List[str] = []

        # --- RECURSIÓN ---
        if recursions:
            reasoning.append(
                f"Detected {len(recursions)} recursive calls in '{name}'.")
            pred = _detect_recursive(info, has_loops=(len(loops) > 0))
            pred["reasoning"] = reasoning + pred["reasoning"]
            out["procedures"][name] = pred
            continue

        # --- BUCLES ---
        if loops:
            reasoning.append(
                f"Detected {len(loops)} loop(s). Adjusted nesting = {max_nesting}.")
            uses_n = False
            for lp in loops:
                s, e = lp.get("start"), lp.get("end")
                if _mentions_symbol(s, "n") or _mentions_symbol(e, "n"):
                    uses_n = True

            theta = _nesting_to_theta(max_nesting)
            if uses_n:
                reasoning.append(
                    "Bounds reference 'n', assuming canonical loop growth.")
                big_theta, big_o = theta, theta
                big_omega = "Theta(n)" if max_nesting == 1 else theta
            else:
                reasoning.append(
                    "Symbol 'n' not seen, using generic n^k heuristic.")
                big_theta, big_o, big_omega = theta, theta, "Theta(1)"

            out["procedures"][name] = {
                "big_o": big_o, "big_omega": big_omega, "big_theta": big_theta,
                "cotas_fuertes": f"c1*n^{max_nesting} <= T(n) <= c2*n^{max_nesting}",
                "recurrence": None, "reasoning": reasoning,
            }
            continue

        # --- CONSTANTE ---
        reasoning.append("No loops or recursion detected.")
        out["procedures"][name] = {
            "big_o": "Theta(1)", "big_omega": "Theta(1)", "big_theta": "Theta(1)",
            "cotas_fuertes": "O(1)", "recurrence": None, "reasoning": reasoning,
        }

    return out

# --- HELPERS ---


def _mentions_symbol(node: Any, symbol: str) -> bool:
    if node is None:
        return False

    def stringify(n):
        if isinstance(n, dict):
            if n.get("type") in ("Identifier", "LValue"):
                return n.get("name", "")
            s = ""
            for v in n.values():
                if isinstance(v, (list, dict)):
                    s += stringify(v) + " "
            return s
        return str(n)
    return symbol.lower() in stringify(node).lower()


def _detect_recursive(info: Dict[str, Any], has_loops: bool) -> Dict[str, Any]:
    recs = info.get("recursions", [])
    if not recs:
        return _unknown_recursion()

    # Reconstrucción de argumentos a texto para análisis
    args_txt_all = []

    def txt(a):
        if isinstance(a, dict):
            t = a.get("type")
            if t in ("Identifier", "LValue"):
                return a.get("name", "")
            if t == "Number":
                return str(a.get("value", ""))
            if t == "BinOp":
                # Si el operador falta, asumimos espacio o + para no romper el string
                op = a.get("op") if a.get("op") else " "
                return f"({txt(a.get('left'))} {op} {txt(a.get('right'))})"
            if t == "Unary":
                return f"{a.get('op')}{txt(a.get('expr'))}"
        return str(a)

    for r in recs:
        for arg in r.get("args", []):
            s = txt(arg)
            args_txt_all.append(s)

    joined = " ".join(args_txt_all).lower()

    # 1. DIVIDE Y VENCERÁS (n/2, mid)
    if "/2" in joined or "mid" in joined or "mitad" in joined:
        if has_loops:
            return {"big_o": "Theta(n log n)", "big_theta": "Theta(n log n)", "big_omega": "Theta(n log n)",
                    "recurrence": "T(n) = 2T(n/2) + O(n)", "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
                    "reasoning": ["Recursive args indicate division (n/2).", "Master Theorem Case 2."]}
        else:
            return {"big_o": "Theta(log n)", "big_theta": "Theta(log n)", "big_omega": "Theta(1)",
                    "recurrence": "T(n) = T(n/2) + O(1)", "cotas_fuertes": "c1*log(n) <= T(n) <= c2*log(n)",
                    "reasoning": ["Recursive args indicate division (n/2).", "Master Theorem Case 1."]}

    # 2. FIBONACCI (Patrón de resta múltiple: n-1 Y n-2)
    # Regex relajado: busca 'n' seguido eventualmente de '1' y 'n' seguido de '2'
    # Esto atrapa "n-1" "n - 1" "(n-1)" etc.
    has_n1 = bool(re.search(r"n.*1", joined))
    has_n2 = bool(re.search(r"n.*2", joined))

    if has_n1 and has_n2:
        return {"big_o": "Theta(phi^n)", "big_theta": "Theta(phi^n)", "big_omega": "Theta(phi^n)",
                "recurrence": "T(n) = T(n-1) + T(n-2)", "cotas_fuertes": "T(n) = Theta(1.618^n)",
                "reasoning": [f"Calls detected with (n-1) and (n-2). Args: {joined}", "Characteristic equation r^2 - r - 1 = 0"]}

    # 3. LINEAL (n-1)
    if has_n1 or "n" in joined:
        return {"big_o": "Theta(n)", "big_theta": "Theta(n)", "big_omega": "Theta(n)",
                "recurrence": "T(n) = T(n-1) + c", "cotas_fuertes": "T(n) = Theta(n)",
                "reasoning": ["Recursive step reduces by constant (n-1).", "Linear recursion depth."]}

    return _unknown_recursion()


def _unknown_recursion():
    return {"big_o": "Theta(?)", "big_theta": "Theta(?)", "big_omega": "Theta(?)",
            "cotas_fuertes": "unknown", "recurrence": None, "reasoning": ["Unknown pattern"]}
