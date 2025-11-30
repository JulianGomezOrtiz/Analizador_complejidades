from typing import Dict, Any, List


def analyze_ast_for_patterns(ast: Dict[str, Any]) -> Dict[str, Any]:
    procedures = {}
    if not ast or not isinstance(ast, dict):
        return {"procedures": {}}

    procs_list = ast.get("procedures", [])

    for proc in procs_list:
        proc_name = proc.get("name")
        body = proc.get("body", [])

        # Pattern Analyzer
        analyzer = ProcAnalyzer(proc_name)
        analyzer.visit(body)

        # Cost Reporter
        cost_reporter = CostReporter()
        cost_reporter.visit(body)

        procedures[proc_name] = {
            "loops": analyzer.loops,
            "recursions": analyzer.recursions,
            "calls": analyzer.calls,
            "max_nesting": analyzer.max_nesting,
            "cost_report": {
                "total_ops": cost_reporter.total_ops,
                "breakdown": cost_reporter.ops_breakdown
            }
        }

    return {"procedures": procedures}


class ProcAnalyzer:
    def __init__(self, proc_name):
        self.proc_name = proc_name
        self.loops = []
        self.recursions = []
        self.calls = []
        self.max_nesting = 0
        self.current_nesting = 0

    def visit(self, node):
        # 1. Iterar listas (ej: body, args)
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        # 2. Ignorar primitivos
        if not isinstance(node, dict):
            return

        typ = node.get("type")

        # --- DETECTAR BUCLES ---
        is_loop = typ in ("For", "While", "Repeat")
        if is_loop:
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)

            if typ == "For":
                self.loops.append({
                    "type": "For",
                    "var": node.get("var"),
                    "start": node.get("start"),
                    "end": node.get("end"),
                    "step": node.get("step"),
                    "nesting": self.current_nesting
                })
            else:
                self.loops.append(
                    {"type": typ, "nesting": self.current_nesting})

        # --- DETECTAR LLAMADAS ---
        if typ == "Call":
            name = node.get("name")
            args = node.get("args", [])
            if name == self.proc_name:
                self.recursions.append({"args": args})
            else:
                self.calls.append({"name": name, "args": args})
            # No retornamos aquí, dejamos que el crawler visite los argumentos abajo

        # --- CRAWLER UNIVERSAL (Fuerza Bruta) ---
        # Visitamos TODOS los valores del diccionario, sin importar la clave.
        # Esto entra en 'value', 'left', 'right', 'cond', 'then', 'body', 'args', etc.
        for key, value in node.items():
            # Evitamos metadatos simples para eficiencia
            if key in ("type", "name", "var", "op", "param_type"):
                continue

            self.visit(value)

        # Restaurar nesting
        if is_loop:
            self.current_nesting -= 1


class CostReporter:
    """
    Cuenta operaciones elementales para estimar el costo base (sin multiplicar por N).
    Útil para comparar constantes ocultas.
    """
    def __init__(self):
        self.total_ops = 0
        self.ops_breakdown = {
            "assign": 0, 
            "math": 0, 
            "cmp": 0, 
            "access": 0, 
            "call": 0,
            "control": 0
        }

    def visit(self, node):
        if isinstance(node, list):
            for item in node:
                self.visit(item)
            return

        if not isinstance(node, dict):
            return

        typ = node.get("type")
        
        if typ == "Assign":
            self._add("assign")
        elif typ in ("BinOp", "Unary"):
            self._add("math")
        elif typ == "ArrayAccess":
            self._add("access")
        elif typ == "Call":
            self._add("call")
        elif typ in ("If", "For", "While", "Repeat"):
            self._add("control")
            
        # Recurse
        for key, value in node.items():
            if key not in ("type", "name", "var", "op"):
                self.visit(value)

    def _add(self, category):
        self.total_ops += 1
        self.ops_breakdown[category] += 1
