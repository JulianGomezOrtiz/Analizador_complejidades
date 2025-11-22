"""
Motor de complejidad:
Produce O, Ω, Θ de manera heurística basándose en:
- loops anidados (corrige anidamiento inflado)
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

    if proc_name:
        targets = {proc_name: procs[proc_name]}
    else:
        targets = procs

    out = {"procedures": {}}

    for name, info in targets.items():
        loops = info.get("loops", [])
        recursions = info.get("recursions", [])
        calls = info.get("calls", [])

        # --- CORRECCIÓN 1: Sanity Check de Nesting ---
        # Si max_nesting dice 3 pero solo hay 2 loops totales, es imposible que sea n^3.
        # Ajustamos max_nesting al número real de bucles para evitar contar IFs/Blocks extra.
        raw_nesting = info.get("max_nesting", 0)
        loop_count = len(loops)
        max_nesting = min(raw_nesting, loop_count) if loop_count > 0 else 0

        # Caso especial: Si raw_nesting era > 0 pero clamp bajó, confiamos en raw si es razonable
        # (Esto ayuda si el analyzer cuenta bucles implícitos, pero para CountPairs queremos 2)
        if raw_nesting > 0 and loop_count >= raw_nesting:
            max_nesting = raw_nesting

        reasoning: List[str] = []

        # ============================================================================
        # RECURSIÓN
        # ============================================================================
        if recursions:
            reasoning.append(f"Detected recursive calls in '{name}'.")
            # Pasamos 'loops' para distinguir entre MergeSort (loops=True) y BinarySearch (loops=False)
            pred = _detect_recursive(info, has_loops=(len(loops) > 0))
            pred["reasoning"].extend(reasoning)
            out["procedures"][name] = pred
            continue

        # ============================================================================
        # LOOPS
        # ============================================================================
        if loops:
            reasoning.append(
                f"Detected {len(loops)} loop(s). Adjusted nesting = {max_nesting}."
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
        # SIN LOOPS NI RECURSIÓN (O(1))
        # ============================================================================
        reasoning.append("No loops or recursion → constant or call-dominated.")

        if calls:
            out["procedures"][name] = {
                "big_o": "Theta(1)",
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


def _detect_recursive(info: Dict[str, Any], has_loops: bool) -> Dict[str, Any]:
    recs = info.get("recursions", [])
    if not recs:
        return _unknown_recursion()

    # Analizamos todos los argumentos de las llamadas recursivas
    # para encontrar patrones (n-1, n/2, mid, etc)
    args_txt_all = []

    def txt(a):
        if isinstance(a, dict):
            t = a.get("type")
            if t == "Identifier":
                return a.get("name", "")
            if t == "Number":
                return str(a.get("value", ""))
            if t == "BinOp":
                # Manejo robusto de operadores nulos
                op = a.get("op") if a.get("op") else "+"
                return f"({txt(a.get('left'))}{op}{txt(a.get('right'))})"
            if t == "Unary":
                return f"{a.get('op')}{txt(a.get('expr'))}"
        return str(a)

    for r in recs:
        for arg in r.get("args", []):
            args_txt_all.append(txt(arg))

    joined = " ".join(args_txt_all).lower()

    # ------ 1. DIVIDE Y VENCERÁS (BinarySearch vs MergeSort) ------
    # Detectar patrones: "/2", "mid", "mitad"
    if "/2" in joined or "mid" in joined:
        # CORRECCIÓN 2: Distinguir Logarítmico vs Lineal-Logarítmico
        if has_loops:
            # Tiene loops (ej. Merge, Partition) -> T(n) = 2T(n/2) + n -> O(n log n)
            return {
                "big_o": "Theta(n log n)",
                "big_omega": "Theta(n log n)",
                "big_theta": "Theta(n log n)",
                "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
                "recurrence": "T(n) = 2T(n/2) + O(n)",
                "reasoning": ["Recursive args indicate division.", "Loops detected in body (Merge/Partition).", "Master Theorem Case 2."],
            }
        else:
            # NO tiene loops (ej. BinarySearch) -> T(n) = T(n/2) + c -> O(log n)
            return {
                "big_o": "Theta(log n)",
                # Mejor caso O(1) si encuentra al inicio
                "big_omega": "Theta(1)",
                "big_theta": "Theta(log n)",  # Caso promedio
                "cotas_fuertes": "c1*log(n) <= T(n) <= c2*log(n)",
                "recurrence": "T(n) = T(n/2) + O(1)",
                "reasoning": ["Recursive args indicate division.", "No loops in body -> Cost per step is constant.", "Master Theorem Case 1."],
            }

    # ------ 2. FIBONACCI (n-1 y n-2) ------
    # CORRECCIÓN 3: Detección robusta de ambas ramas
    has_n_minus_1 = bool(re.search(r"n\s*[-+]\s*1", joined))
    has_n_minus_2 = bool(re.search(r"n\s*[-+]\s*2", joined))

    if has_n_minus_1 and has_n_minus_2:
        return {
            "big_o": "Theta(phi^n)",
            "big_omega": "Theta(phi^n)",
            "big_theta": "Theta(phi^n)",
            "cotas_fuertes": "T(n) = Theta(1.618^n)",
            "recurrence": "T(n) = T(n-1) + T(n-2)",
            "reasoning": ["Calls T(n-1) and T(n-2).", "Characteristic equation: r^2 - r - 1 = 0.", "Exponential growth."],
        }

    # ------ 3. LINEAL (n-1 o n+1) ------
    if has_n_minus_1 or "n" in joined:  # Fallback si vemos 'n' en recursion
        return {
            "big_o": "Theta(n)",
            "big_omega": "Theta(n)",
            "big_theta": "Theta(n)",
            "cotas_fuertes": "T(n) = Theta(n)",
            "recurrence": "T(n) = T(n-1) + O(1)",
            "reasoning": ["Recursive step reduces by constant (n-1).", "Linear recursion depth."],
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
