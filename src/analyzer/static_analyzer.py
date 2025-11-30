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
        self.geometric_vars = set()

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

        # --- RASTREO DE VARIABLES GEOMÉTRICAS (Global en el procedimiento) ---
        if typ == "Assign":
            target = node.get("target")
            val = node.get("value")
            if isinstance(target, dict) and target.get("name"):
                name = target.get("name")
                print(f"DEBUG: Assigning to {name}, val: {val}")
                has_div = self._contains_div_mult(val)
                uses_geo = self._uses_vars(val, self.geometric_vars)
                if has_div or uses_geo:
                    print(f"DEBUG: Adding {name} to geometric_vars (HasDiv={has_div}, UsesGeo={uses_geo})")
                    self.geometric_vars.add(name)

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
            elif typ in ("While", "Repeat"):
                # Detectar actualizaciones geométricas en el cuerpo
                geometric_update = False
                cond_vars = self._extract_vars(node.get("cond"))
                
                # Rastreo simple de variables "geométricas" (derivadas de div/mult)
                # Usamos un set local para el bucle, pero inicializado con las globales
                loop_geometric_vars = self.geometric_vars.copy()
                
                # Escanear cuerpo
                body = node.get("body", [])
                if isinstance(body, list):
                    # Pasada 1: Identificar variables calculadas con div/mult
                    self._scan_for_geometric_vars(body, loop_geometric_vars)
                    
                    # Pasada 2: Verificar si variables de condición dependen de ellas
                    if self._check_geometric_dependency(body, cond_vars, loop_geometric_vars):
                        geometric_update = True

                self.loops.append({
                    "type": typ,
                    "cond": node.get("cond"),
                    "nesting": self.current_nesting,
                    "geometric_update": geometric_update
                })
            else:
                self.loops.append(
                    {"type": typ, "nesting": self.current_nesting})

        # --- DETECTAR LLAMADAS ---
        if typ == "Call":
            name = node.get("name")
            args = node.get("args", [])
            
            # Verificar si los argumentos usan variables geométricas
            uses_geometric = False
            print(f"DEBUG: Checking call {name}, GeometricVars: {self.geometric_vars}")
            for arg in args:
                is_used = self._uses_vars(arg, self.geometric_vars)
                print(f"DEBUG: Arg {arg} uses_vars={is_used}")
                if is_used:
                    uses_geometric = True
                    break
            
            if name == self.proc_name:
                self.recursions.append({"args": args, "uses_geometric": uses_geometric})
            else:
                self.calls.append({"name": name, "args": args})

        # --- CRAWLER UNIVERSAL ---
        for key, value in node.items():
            if key in ("type", "name", "var", "op", "param_type"):
                continue
            self.visit(value)

        if is_loop:
            self.current_nesting -= 1

    def _extract_vars(self, node):
        vars_found = set()
        if isinstance(node, dict):
            if node.get("type") in ("Identifier", "LValue"):
                vars_found.add(node.get("name"))
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    vars_found.update(self._extract_vars(v))
        elif isinstance(node, list):
            for item in node:
                vars_found.update(self._extract_vars(item))
        return vars_found

    def _scan_for_geometric_vars(self, block, geometric_vars):
        if not block: return
        for stmt in block:
            if stmt.get("type") == "Assign":
                target = stmt.get("target")
                val = stmt.get("value")
                if isinstance(target, dict) and target.get("name"):
                    name = target.get("name")
                    has_div = self._contains_div_mult(val)
                    uses_geo = self._uses_vars(val, geometric_vars)
                    
                    if has_div or uses_geo:
                        geometric_vars.add(name)
            
            elif stmt.get("type") == "If":
                self._scan_for_geometric_vars(stmt.get("then"), geometric_vars)
                self._scan_for_geometric_vars(stmt.get("else_"), geometric_vars)

    def _check_geometric_dependency(self, block, cond_vars, geometric_vars):
        if not block: return False
        for stmt in block:
            if stmt.get("type") == "Assign":
                target = stmt.get("target")
                val = stmt.get("value")
                if isinstance(target, dict) and target.get("name") in cond_vars:
                    # Si asignamos a una variable de loop algo que usa una variable geométrica
                    if self._uses_vars(val, geometric_vars) or self._contains_div_mult(val):
                        return True
            
            elif stmt.get("type") == "If":
                if self._check_geometric_dependency(stmt.get("then"), cond_vars, geometric_vars) or \
                   self._check_geometric_dependency(stmt.get("else_"), cond_vars, geometric_vars):
                    return True
        return False

    def _uses_vars(self, expr, vars_set):
        if not isinstance(expr, dict): return False
        if expr.get("type") in ("Identifier", "LValue"):
            return expr.get("name") in vars_set
        
        for k, v in expr.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list):
                    for i in v: 
                        if self._uses_vars(i, vars_set): return True
                else:
                    if self._uses_vars(v, vars_set): return True
        return False

    def _contains_div_mult(self, expr):
        if not isinstance(expr, dict): return False
        
        typ = expr.get("type")
        if typ == "BinOp":
            op = str(expr.get("op"))
            print(f"DEBUG: Checking op {op}")
            if op in ("*", "/", "div"):
                return True
        elif typ == "Unary":
            inner = expr.get("expr")
            print(f"DEBUG: Unary inner: {inner}")
            return self._contains_div_mult(inner)
            
        for k, v in expr.items():
            if isinstance(v, (dict, list)):
                if isinstance(v, list):
                    for i in v: 
                        if self._contains_div_mult(i): return True
                else:
                    if self._contains_div_mult(v): return True
        return False


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
