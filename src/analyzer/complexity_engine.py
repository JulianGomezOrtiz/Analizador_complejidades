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
        # ============================================================================
        # 1. ANÁLISIS RECURSIVO (Técnicas Avanzadas)
        # ============================================================================
        if recursions:
            reasoning.append(
                f"Detectadas {len(recursions)} llamadas recursivas en '{name}'.")
            
            calls = info.get("calls", [])
            has_loops = (len(loops) > 0) or (len(calls) > 0)
            pred = _solve_recurrence(info, has_loops=has_loops)
            
            # Adaptar salida recursiva a estructura multicapa
            complexity_data = {
                "worst_case": pred["big_o"],
                "average_case": pred["big_theta"],
                "best_case": "Omega(1)", # Heurística: Caso base alcanzado inmediatamente
                "big_o": pred["big_o"],       # Legacy support
                "big_theta": pred["big_theta"], # Legacy support
                "big_omega": "Omega(1)"       # Legacy support
            }
            
            pred["complexity"] = complexity_data
            pred["reasoning"] = reasoning + pred["reasoning"]
            
            out["procedures"][name] = pred
            continue

        # ============================================================================
        # 2. ANÁLISIS ITERATIVO (Sumatorias)
        # ============================================================================
        if loops:
            reasoning.append(
                f"Estructura iterativa detectada. Profundidad máxima: {max_nesting}.")

            # --- ANÁLISIS PEOR CASO (Worst Case) ---
            # Basado en max_nesting y tipos de serie
            
            # Detección de Series Aritméticas (Bucles Dependientes)
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
                cond = lp.get("cond")
                geo_update = lp.get("geometric_update", False)
                
                # Check Geometric Series (Step > 1 multiplicative)
                if (step and _is_multiplicative_step(step)) or geo_update:
                    is_geometric = True
                    reasoning.append(f"  -> Paso multiplicativo detectado en bucle '{lp.get('var') or 'WHILE'}'. Serie Geométrica (log n).")

                # Chequear si usa 'n'
                if _mentions_symbol(s, "n") or _mentions_symbol(e, "n") or _mentions_symbol(cond, "n"):
                    uses_n = True

                # Chequear si depende de otro bucle (Serie Aritmética)
                for var in dependent_vars:
                    if var != lp.get("var"):  # No contar autoreferencia
                        if _mentions_symbol(s, var) or _mentions_symbol(e, var):
                            is_dependent = True
                            reasoning.append(
                                f"  -> Dependencia detectada: El bucle '{lp.get('var')}' depende de '{var}'.")
                        
                        if step and _mentions_symbol(step, var):
                            is_harmonic = True
                            reasoning.append(f"  -> Paso dependiente de variable externa '{var}'. Posible Serie Armónica.")

            # Calculo Base Peor Caso
            theta_worst = _nesting_to_theta(max_nesting)
            
            if is_geometric:
                if max_nesting == 1:
                    theta_worst = "Theta(log n)"
                else:
                    theta_worst = f"Theta(n^{max_nesting-1} log n)".replace("^", "**")
                reasoning.append(f"  -> [Peor Caso] Reducción logarítmica por serie geométrica: {theta_worst}")

            elif is_harmonic:
                theta_worst = f"Theta(n^{max_nesting-1} log n)".replace("^", "**")
                reasoning.append(f"  -> [Peor Caso] Suma armónica: {theta_worst}")

            elif is_dependent and max_nesting >= 2:
                reasoning.append("  -> [Peor Caso] Serie Aritmética (Triangular) -> n^2.")
                # Se mantiene n^k

            elif not uses_n:
                reasoning.append("  -> [Peor Caso] 'n' no encontrado en límites. Posible O(1).")
                theta_worst = "Theta(1)"

            worst_case = theta_worst.replace("Theta", "O")
            
            # --- ANÁLISIS MEJOR CASO (Best Case) ---
            # Heurística: Cadenas de bucles FOR puros (inevitables).
            # Los bucles WHILE/REPEAT se asumen evitables (0 iteraciones o 1 check) en el mejor caso.
            
            max_unavoidable_depth = 0
            current_chain_depth = 0
            loop_stack = [] # (type, nesting)
            
            # Reconstrucción simplificada de cadenas basada en nesting
            # Asumimos que los loops vienen en orden DFS
            prev_nesting = 0
            
            # Mapa de nesting -> es_for_puro
            # Si un nivel es WHILE, invalida ese nivel y sus hijos para el mejor caso
            level_is_unavoidable = {} 
            
            for lp in loops:
                nesting = lp.get("nesting", 0)
                typ = lp.get("type", "")
                
                # Si subimos de nivel (nesting <= prev), limpiar niveles superiores
                if nesting <= prev_nesting:
                    # No es necesario limpiar explícitamente si sobrescribimos, 
                    # pero conceptualmente cerramos scopes.
                    pass
                
                # Determinar si este nivel es inevitable
                # Es inevitable SI es FOR Y su padre (nesting-1) también era inevitable (o es nivel 1)
                parent_inevitable = True
                if nesting > 1:
                    parent_inevitable = level_is_unavoidable.get(nesting - 1, False)
                
                is_for = (typ == "For")
                is_inevitable = is_for and parent_inevitable
                
                level_is_unavoidable[nesting] = is_inevitable
                
                if is_inevitable:
                    max_unavoidable_depth = max(max_unavoidable_depth, nesting)
                
                prev_nesting = nesting

            if max_unavoidable_depth == 0:
                best_case = "Omega(1)"
                reasoning.append("  -> [Mejor Caso] No hay bucles FOR inevitables. Omega(1).")
            else:
                best_case = _nesting_to_theta(max_unavoidable_depth).replace("Theta", "Omega")
                reasoning.append(f"  -> [Mejor Caso] Cadena de {max_unavoidable_depth} bucles FOR inevitables. {best_case}.")

            # --- ANÁLISIS CASO PROMEDIO (Average Case) ---
            # Por defecto igual al Peor Caso
            average_case = theta_worst
            
            out["procedures"][name] = {
                "worst_case": worst_case,
                "best_case": best_case,
                "average_case": average_case,
                "big_o": worst_case,          # Legacy
                "big_omega": best_case,       # Legacy
                "big_theta": average_case,    # Legacy
                "complexity": {
                    "worst_case": worst_case,
                    "best_case": best_case,
                    "average_case": average_case,
                    "big_o": worst_case,
                    "big_omega": best_case,
                    "big_theta": average_case
                },
                "cotas_fuertes": f"c1*g(n) <= T(n) <= c2*g(n)",
                "recurrence": None, 
                "reasoning": reasoning,
            }
            continue

        # --- CONSTANTE ---
        reasoning.append(
            "No se detectaron estructuras de control dependientes de N.")
        const_comp = {
            "worst_case": "Theta(1)",
            "best_case": "Theta(1)",
            "average_case": "Theta(1)",
            "big_o": "Theta(1)",
            "big_omega": "Theta(1)",
            "big_theta": "Theta(1)"
        }
        out["procedures"][name] = {
            "worst_case": "Theta(1)",
            "best_case": "Theta(1)",
            "average_case": "Theta(1)",
            "big_o": "Theta(1)",
            "big_omega": "Theta(1)",
            "big_theta": "Theta(1)",
            "complexity": const_comp,
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
    # Verificar si hay variables geométricas en los argumentos
    uses_geometric = any(r.get("uses_geometric") for r in recs)
    
    # Heurística para QuickSort: argumentos con +1 y -1 (partition)
    has_partition_pattern = ("-1" in joined and "+1" in joined) or ("- 1" in joined and "+ 1" in joined)
    
    if "/2" in joined or "mid" in joined or "mitad" in joined or uses_geometric or has_partition_pattern:
        b = 2  # Asumimos división por 2 típica

        # Determinar f(n) basado en si hay bucles en el cuerpo
        if has_loops:
            # f(n) = Theta(n) -> Merge Sort, Quick Sort
            
            # Si es patrón de partición (QuickSort), el peor caso es n^2
            if has_partition_pattern:
                return {
                    "big_o": "O(n^2)", 
                    "big_theta": "Theta(n log n)", 
                    "big_omega": "Omega(n log n)",
                    "worst_case": "O(n^2)", "average_case": "Theta(n log n)", "best_case": "Omega(n log n)",
                    "recurrence": f"T(n) = T(q-1) + T(n-q) + O(n)",
                    "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n^2",
                    "reasoning": ["Patrón de partición detectado (QuickSort).", "Promedio: Theta(n log n), Peor: O(n^2)."]
                }
            
            return {
                "big_o": "O(n log n)", "big_theta": "Theta(n log n)", "big_omega": "Omega(n log n)",
                "worst_case": "O(n log n)", "average_case": "Theta(n log n)", "best_case": "Omega(n log n)", # MergeSort siempre es n log n
                "recurrence": f"T(n) = {a}T(n/{b}) + O(n)",
                "cotas_fuertes": "c1*n*log(n) <= T(n) <= c2*n*log(n)",
                "reasoning": [
                    f"Forma del Teorema Maestro: T(n) = aT(n/b) + f(n)",
                    f"  -> a = {a} (llamadas), b = {b} (división)",
                    f"  -> f(n) es O(n) debido a bucles presentes (Merge/Partition).",
                    "  -> Resultado Theta(n log n)"
                ]
            }
        else:
            # f(n) = Theta(1) -> Binary Search
            return {
                "big_o": "O(log n)", "big_theta": "Theta(log n)", "big_omega": "Omega(1)",
                "worst_case": "O(log n)", "average_case": "Theta(log n)", "best_case": "Omega(1)",
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
        phi = (1 + math.sqrt(5)) / 2
        return {
            "big_o": f"O({phi:.3f}^n)", "big_theta": f"Theta({phi:.3f}^n)", "big_omega": "Omega(1)",
            "worst_case": f"O({phi:.3f}^n)", "average_case": f"Theta({phi:.3f}^n)", "best_case": "Omega(1)",
            "recurrence": "T(n) = T(n-1) + T(n-2)",
            "cotas_fuertes": f"T(n) ~ {phi:.3f}^n",
            "reasoning": [
                "Recurrencia Lineal Homogénea de Segundo Orden detectada (Fibonacci).",
                f"  -> La raíz dominante es Phi ({phi:.3f}...) -> Crecimiento Exponencial."
            ]
        }

    # --- CASO 3: RECURSIÓN LINEAL SIMPLE (o Múltiple) ---
    if has_n1 or "n" in joined:
        if a > 1:
            return {
                "big_o": f"O({a}^n)", "big_theta": f"Theta({a}^n)", "big_omega": "Omega(1)",
                "worst_case": f"O({a}^n)", "average_case": f"Theta({a}^n)", "best_case": "Omega(1)",
                "recurrence": f"T(n) = {a}T(n-1) + c",
                "cotas_fuertes": f"T(n) = c*{a}^n",
                "reasoning": [
                    f"Múltiples llamadas recursivas ({a}) reduciendo n en 1.",
                    f"  -> Profundidad n, ramificación {a} -> Complejidad Exponencial O({a}^n)."
                ]
            }
        else:
            # Caso Lineal Simple (T(n) = T(n-1) + c) -> MaxHeapify, Factorial
            return {
                "big_o": "O(n)", "big_theta": "Theta(n)", "big_omega": "Omega(1)",
                "worst_case": "O(n)", "average_case": "Theta(n)", "best_case": "Omega(1)", # Heurística: Caso base o condición falsa
                "recurrence": "T(n) = T(n-1) + c",
                "cotas_fuertes": "T(n) = c*n",
                "reasoning": [
                    "Reducción lineal del problema (T(n-1)).",
                    "  -> Profundidad de la pila de recursión: n",
                    "  -> Costo por nivel: O(1).",
                    "  -> [Mejor Caso] Omega(1) si la condición de recursión falla al inicio."
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
