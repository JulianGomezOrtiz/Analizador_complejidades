"""
Motor de complejidad 2.0 (Razonamiento Formal):
Produce O, Ω, Θ basándose en técnicas formales de las notas de clase:
- Sumatorias y Series (para bucles dependientes).
- Teorema Maestro (identificación de a, b, f(n)).
- Ecuaciones Características (para recurrencias lineales).
"""

from typing import Dict, Any, List
import re
import math


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
        cost_report = info.get("cost_report", {})

        # --- Ajuste de Anidamiento (Sanity Check) ---
        raw_nesting = info.get("max_nesting", 0)
        loop_count = len(loops)
        max_nesting = min(raw_nesting, loop_count) if loop_count > 0 else 0
        if raw_nesting > 0 and loop_count >= raw_nesting:
            max_nesting = raw_nesting

        reasoning: List[str] = []
        if cost_report:
            reasoning.append(f"Costo base estimado (ops elementales): {cost_report.get('total_ops', 0)}")

        # ============================================================================
        # 1. ANÁLISIS RECURSIVO (Técnicas Avanzadas)
        # ============================================================================
        if recursions:
            reasoning.append(
                f"Detectadas {len(recursions)} llamadas recursivas en '{name}'.")
            # Pasamos 'loops' para saber si hay costo de combinación (f(n))
            pred = _solve_recurrence(info, has_loops=(len(loops) > 0))
            pred["reasoning"] = reasoning + pred["reasoning"]
            out["procedures"][name] = pred
            continue

        # ============================================================================
        # 2. ANÁLISIS ITERATIVO (Sumatorias)
        # ============================================================================
        if loops:
            reasoning.append(
                f"Estructura iterativa detectada. Profundidad máxima: {max_nesting}.")

            # Detección de Series Aritméticas (Bucles Dependientes)
            # Ejemplo: FOR j <- 1 TO i (depende de i)
            dependent_vars = set()
            is_dependent = False
            uses_n = False
            is_geometric = False
            is_harmonic = False

            # Primera pasada: registrar variables de bucles
            for lp in loops:
                if lp.get("var"):
                    dependent_vars.add(lp.get("var"))

            # Segunda pasada: verificar dependencias y tipos de serie
            for lp in loops:
                s, e = lp.get("start"), lp.get("end")
                step = lp.get("step")
                
                # Check Geometric Series (Step > 1 multiplicative)
                if step and _is_multiplicative_step(step):
                    is_geometric = True
                    reasoning.append(f"  -> Paso multiplicativo detectado en bucle '{lp.get('var')}'. Serie Geométrica (log n).")

                # Chequear si usa 'n'
                if _mentions_symbol(s, "n") or _mentions_symbol(e, "n"):
                    uses_n = True

                # Chequear si depende de otro bucle (Serie Aritmética)
                for var in dependent_vars:
                    if var != lp.get("var"):  # No contar autoreferencia
                        if _mentions_symbol(s, var) or _mentions_symbol(e, var):
                            is_dependent = True
                            reasoning.append(
                                f"  -> Dependencia detectada: El bucle '{lp.get('var')}' depende de '{var}'.")
                        
                        # Harmonic check: step depends on outer var? 
                        # Or inner loop range is n/i? (Hard to detect with current AST)
                        # Heuristic: if step is variable 'i' from outer loop
                        if step and _mentions_symbol(step, var):
                            is_harmonic = True
                            reasoning.append(f"  -> Paso dependiente de variable externa '{var}'. Posible Serie Armónica.")

            theta = _nesting_to_theta(max_nesting)

            if is_geometric:
                # Reduce complexity by log factor for each geometric loop
                # Simplified: assuming 1 geometric loop reduces n to log n
                # If max_nesting is 1 -> log n
                # If max_nesting is 2 -> n log n (if one is geometric)
                if max_nesting == 1:
                    big_theta = "Theta(log n)"
                else:
                    big_theta = f"Theta(n^{max_nesting-1} log n)".replace("^", "**")
                
                big_o, big_omega = big_theta, big_theta
                reasoning.append(f"  -> Aplicando reducción logarítmica por serie geométrica: {big_theta}")

            elif is_harmonic:
                # Harmonic series sum(1/i) is log n.
                # Usually nested inside an n loop -> n log n.
                big_theta = f"Theta(n^{max_nesting-1} log n)".replace("^", "**")
                big_o, big_omega = big_theta, big_theta
                reasoning.append(f"  -> Aplicando suma armónica: {big_theta}")

            elif is_dependent and max_nesting >= 2:
                reasoning.append(
                    "  -> Identificado patrón de Serie Aritmética (Triangular).")
                reasoning.append(
                    f"  -> Aplicando fórmula de suma: Sum(i) = n(n+1)/2 = Theta(n^2).")
                # La complejidad sigue siendo n^k, pero el razonamiento es más formal
                big_theta, big_o, big_omega = theta, theta, theta

            elif uses_n:
                reasoning.append(
                    "  -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).")
                reasoning.append("  -> Producto cartesiano de iteraciones.")
                big_theta, big_o = theta, theta
                big_omega = "Theta(n)" if max_nesting == 1 else theta
            else:
                reasoning.append(
                    "  -> Símbolo 'n' no encontrado en límites. Posible O(1) o variable desconocida.")
                big_theta, big_o, big_omega = theta, theta, "Theta(1)"

            out["procedures"][name] = {
                "big_o": big_o, "big_omega": big_omega, "big_theta": big_theta,
                "cotas_fuertes": f"c1*g(n) <= T(n) <= c2*g(n)",
                "recurrence": None, "reasoning": reasoning,
            }
            continue

        # --- CONSTANTE ---
        reasoning.append(
            "No se detectaron estructuras de control dependientes de N.")
        out["procedures"][name] = {
            "big_o": "Theta(1)", "big_omega": "Theta(1)", "big_theta": "Theta(1)",
            "cotas_fuertes": "T(n) = c", "recurrence": None, "reasoning": reasoning,
        }

    return out

# =============================================================================
# SOLVERS MATEMÁTICOS
# =============================================================================


def _solve_recurrence(info: Dict[str, Any], has_loops: bool) -> Dict[str, Any]:
    recs = info.get("recursions", [])
    if not recs:
        return _unknown_recursion()

    # Extraer argumentos para análisis
    args_txt_all = []

    def txt(a):
        if isinstance(a, dict):
            t = a.get("type")
            if t in ("Identifier", "LValue"):
                return a.get("name", "")
            if t == "Number":
                return str(a.get("value", ""))
            if t == "BinOp":
                op = a.get("op") if a.get("op") else "+"
                return f"({txt(a.get('left'))}{op}{txt(a.get('right'))})"
            if t == "Unary":
                return f"{a.get('op')}{txt(a.get('expr'))}"
        return str(a)

    for r in recs:
        for arg in r.get("args", []):
            args_txt_all.append(txt(arg))

    joined = " ".join(args_txt_all).lower()

    # Parametros estimados para Teorema Maestro: T(n) = aT(n/b) + f(n)
    a = len(recs)  # Número de llamadas recursivas

    # --- CASO 1: DIVIDE Y VENCERÁS (Teorema Maestro) ---
    if "/2" in joined or "mid" in joined or "mitad" in joined:
        b = 2  # Asumimos división por 2 típica

        # Determinar f(n) basado en si hay bucles en el cuerpo
        if has_loops:
            # f(n) = Theta(n) -> Merge Sort, Quick Sort
            # Caso 2: n^(log_b a) = n^1 vs f(n) = n -> O(n log n)
            return {
                "big_o": "Theta(n log n)", "big_theta": "Theta(n log n)", "big_omega": "Theta(n log n)",
                "recurrence": f"T(n) = {a}T(n/{b}) + O(n)",
                "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
                "reasoning": [
                    f"Forma del Teorema Maestro: T(n) = aT(n/b) + f(n)",
                    f"  -> a = {a} (llamadas), b = {b} (división)",
                    f"  -> f(n) es O(n) debido a bucles presentes (Merge/Partition).",
                    f"  -> log_b(a) = log_2({a}) = {1 if a==2 else '?'}",
                    "  -> Caso 2: f(n) es Theta(n^log_b a) * log^k n -> Resultado Theta(n log n)"
                ]
            }
        else:
            # f(n) = Theta(1) -> Binary Search
            # Caso 1: n^(log_b a) vs f(n)=1.
            # Si a=1 (Binary Search) -> n^0 = 1. f(n) = 1. -> O(log n)? No, Case 2 master theorem con k=0.
            return {
                "big_o": "Theta(log n)", "big_theta": "Theta(log n)", "big_omega": "Theta(1)",
                "recurrence": f"T(n) = {a}T(n/{b}) + O(1)",
                "cotas_fuertes": "c1*log(n) <= T(n) <= c2*log(n)",
                "reasoning": [
                    f"Forma del Teorema Maestro: T(n) = {a}T(n/{b}) + O(1)",
                    "  -> No hay bucles significativos fuera de la recursión (f(n) = O(1)).",
                    "  -> Aplicando Teorema Maestro (Caso 2 con k=0 para a=1) -> Theta(log n)."
                ]
            }

    # --- CASO 2: RECURRENCIA LINEAL HOMOGÉNEA (Ecuación Característica) ---
    # Detectar patrones tipo T(n-1) y T(n-2)
    has_n1 = bool(re.search(r"n.*1", joined))  # n-1
    has_n2 = bool(re.search(r"n.*2", joined))  # n-2

    if has_n1 and has_n2:
        # Resolver r^2 - c1*r - c2 = 0
        # Asumimos T(n) = T(n-1) + T(n-2) -> r^2 - r - 1 = 0
        # TODO: Detectar coeficientes reales si es posible. Por ahora asumimos Fibonacci.
        
        # Solver cuadrático
        # r^2 - r - 1 = 0
        phi = (1 + math.sqrt(5)) / 2
        
        return {
            "big_o": f"Theta({phi:.3f}^n)", "big_theta": f"Theta({phi:.3f}^n)", "big_omega": f"Theta({phi:.3f}^n)",
            "recurrence": "T(n) = T(n-1) + T(n-2)",
            "cotas_fuertes": f"T(n) ~ {phi:.3f}^n",
            "reasoning": [
                "Recurrencia Lineal Homogénea de Segundo Orden detectada.",
                "  -> Forma: c1*T(n-1) + c2*T(n-2)",
                "  -> Ecuación Característica: r^2 - r - 1 = 0",
                "  -> Raíces: (1 ± sqrt(5)) / 2",
                f"  -> La raíz dominante es Phi ({phi:.3f}...) -> Crecimiento Exponencial."
            ]
        }

    # --- CASO 3: RECURSIÓN LINEAL SIMPLE (o Múltiple) ---
    if has_n1 or "n" in joined:
        if a > 1:
            return {
                "big_o": f"Theta({a}^n)", "big_theta": f"Theta({a}^n)", "big_omega": f"Theta({a}^n)",
                "recurrence": f"T(n) = {a}T(n-1) + c",
                "cotas_fuertes": f"T(n) = c*{a}^n",
                "reasoning": [
                    f"Múltiples llamadas recursivas ({a}) reduciendo n en 1.",
                    f"  -> Forma: T(n) = {a}T(n-1) + c",
                    f"  -> Profundidad n, ramificación {a} -> Complejidad Exponencial O({a}^n)."
                ]
            }
        else:
            return {
                "big_o": "Theta(n)", "big_theta": "Theta(n)", "big_omega": "Theta(n)",
                "recurrence": "T(n) = T(n-1) + c",
                "cotas_fuertes": "T(n) = c*n",
                "reasoning": [
                    "Reducción lineal del problema (T(n-1)).",
                    "  -> Profundidad de la pila de recursión: n",
                    "  -> Costo por nivel: O(1) (sin bucles anidados detectados)."
                ]
            }

    return _unknown_recursion()


def _unknown_recursion():
    return {"big_o": "Theta(?)", "big_theta": "Theta(?)", "big_omega": "Theta(?)",
            "cotas_fuertes": "desconocido", "recurrence": None, "reasoning": ["Patrón de recursión no reconocido."]}


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

def _is_multiplicative_step(step_node: Any) -> bool:
    """Detecta si el paso es * 2, / 2, etc."""
    if not isinstance(step_node, dict): return False
    # Si es un BinOp con * o /
    if step_node.get("type") == "BinOp":
        op = step_node.get("op")
        return op in ("*", "/", "div")
    return False
