from typing import Dict, Any, List


def analyze_ast_for_patterns(ast: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recorre el AST para extraer métricas clave:
    - Bucles (anidamiento, rangos)
    - Recursión (llamadas a sí mismo)
    - Llamadas externas
    """
    procedures = {}

    # Si el AST es una lista (caso raro), buscar dicts dentro
    procs_list = ast.get("procedures", []) if isinstance(ast, dict) else []

    for proc in procs_list:
        proc_name = proc.get("name")
        body = proc.get("body", [])

        # Analizadores de estado
        analyzer = ProcAnalyzer(proc_name)
        analyzer.visit(body)

        procedures[proc_name] = {
            "loops": analyzer.loops,
            "recursions": analyzer.recursions,
            "calls": analyzer.calls,
            "max_nesting": analyzer.max_nesting
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
        if isinstance(node, list):
            for stmt in node:
                self.visit(stmt)
            return

        if not isinstance(node, dict):
            return

        typ = node.get("type")

        # --- MANEJO DE BUCLES ---
        if typ in ("For", "While", "Repeat"):
            self.current_nesting += 1
            self.max_nesting = max(self.max_nesting, self.current_nesting)

            # Guardar info del loop
            if typ == "For":
                self.loops.append({
                    "type": "For",
                    "var": node.get("var"),
                    "start": node.get("start"),
                    "end": node.get("end"),
                    "nesting": self.current_nesting
                })
            else:
                self.loops.append(
                    {"type": typ, "nesting": self.current_nesting})

            # Visitar cuerpo
            self.visit(node.get("body", []))
            self.current_nesting -= 1
            return

        # --- MANEJO DE CONTROL DE FLUJO (IF) ---
        if typ == "If":
            # No aumentamos nesting de bucles, pero visitamos las ramas
            self.visit(node.get("then", []))
            self.visit(node.get("else_", []))
            return

        # --- MANEJO DE LLAMADAS (RECURSIVAS O EXTERNAS) ---
        if typ == "Call":
            name = node.get("name")
            args = node.get("args", [])
            if name == self.proc_name:
                self.recursions.append({"args": args})
            else:
                self.calls.append({"name": name, "args": args})
            # Revisar argumentos por si hay llamadas anidadas: f(g(x))
            for arg in args:
                self.visit(arg)
            return

        # --- EXPRESIONES Y OTROS NODOS ---
        # Hay que visitar hijos para encontrar llamadas ocultas (ej: Return Fib(n-1))

        if typ == "Return":
            self.visit(node.get("value"))

        elif typ == "Assign":
            self.visit(node.get("value"))

        elif typ == "BinOp":
            self.visit(node.get("left"))
            self.visit(node.get("right"))

        elif typ == "Unary":
            self.visit(node.get("expr"))

        # Caso general: Si tiene cuerpo o lista, visítalos
        if "body" in node:
            self.visit(node["body"])
