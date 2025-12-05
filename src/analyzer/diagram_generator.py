import graphviz
from typing import Dict, Any
import os


class TraceGenerator:
    """
    Generador de Diagramas de Flujo de Control (CFG) de alta calidad.
    - Usa estilos ortogonales.
    - Reconstruye expresiones del AST para las etiquetas.
    - Aplica paleta de colores semántica.
    """

    def __init__(self, ast: Dict[str, Any], output_format='png'):
        self.ast = ast
        self.format = output_format
        self.graph = None
        self.node_count = 0

        # Paleta de Colores "Engineering"
        self.style = {
            # Verde suave
            "start":   {"shape": "Mdiamond", "style": "filled", "fillcolor": "#C5E1A5", "fontname": "Consolas-Bold"},
            # Rojo suave
            "end":     {"shape": "Msquare",  "style": "filled", "fillcolor": "#EF9A9A", "fontname": "Consolas-Bold"},
            # Azul muy claro
            "process": {"shape": "box",      "style": "filled", "fillcolor": "#E3F2FD", "fontname": "Consolas", "penwidth": "0.5"},
            # Amarillo
            "decision": {"shape": "diamond", "style": "filled", "fillcolor": "#FFF59D", "fontname": "Consolas", "height": "0.8"},
            # Azul Loop
            "loop":    {"shape": "hexagon",  "style": "filled", "fillcolor": "#B3E5FC", "fontname": "Consolas-Bold"},
            # Violeta
            "call":    {"shape": "component", "style": "filled", "fillcolor": "#E1BEE7", "fontname": "Consolas"},
            "edge":    {"fontname": "Arial", "fontsize": "10", "color": "#546E7A"}
        }

    def generate(self):
        procs = self.ast.get("procedures", [])
        base_output_dir = os.path.join(os.getcwd(), 'docs', 'diagrams')
        if not os.path.exists(base_output_dir):
            os.makedirs(base_output_dir, exist_ok=True)

        for proc in procs:
            proc_name = proc.get("name", "Unknown")
            # Configuración Global del Grafo
            self.graph = graphviz.Digraph(
                f'cluster_{proc_name}', format=self.format)
            self.graph.attr(
                rankdir='TB',
                splines='ortho',     # Líneas ortogonales (rectas)
                nodesep='0.5',
                ranksep='0.5',
                fontname='Helvetica',
                label=f'CFG: {proc_name}',
                labelloc='t'
            )
            self.node_count = 0

            # --- Inicio ---
            params = ", ".join([p['name'] for p in proc.get('params', [])])
            start_label = f"START\n{proc_name}({params})"
            start_node = self._add_node(start_label, **self.style["start"])

            # --- Cuerpo ---
            last_node = self._visit_block(proc.get("body", []), start_node)

            # --- Fin ---
            end_node = self._add_node("END", **self.style["end"])
            if last_node:
                self.graph.edge(last_node, end_node, **self.style["edge"])

            # --- Render ---
            output_path = os.path.join(base_output_dir, f"{proc_name}_trace")
            try:
                self.graph.render(output_path, cleanup=True)
                print(f" ✨ Diagrama PRO generado: {output_path}.{self.format}")
            except graphviz.backend.ExecutableNotFound:
                print("⚠️ ERROR: Graphviz no está instalado o no está en el PATH.")

    def _add_node(self, label, **kwargs):
        node_id = f"node_{self.node_count}"
        self.node_count += 1
        # Limpiar etiqueta para evitar errores de sintaxis DOT
        clean_label = str(label).replace(":", "∶")
        self.graph.node(node_id, label=clean_label, **kwargs)
        return node_id

    def _visit_block(self, stmts, previous_node):
        current = previous_node
        for stmt in stmts:
            typ = stmt.get("type")

            # 1. ASIGNACIÓN
            if typ == "Assign":
                target = self._expr_to_str(stmt.get('target'))
                value = self._expr_to_str(stmt.get('value'))
                label = f"{target} 🡨 {value}"
                node = self._add_node(label, **self.style["process"])
                self.graph.edge(current, node, **self.style["edge"])
                current = node

            # 2. IF / ELSE
            elif typ == "If":
                cond_txt = self._expr_to_str(stmt.get('cond'))
                cond_node = self._add_node(
                    f"¿{cond_txt}?", **self.style["decision"])
                self.graph.edge(current, cond_node, **self.style["edge"])

                # True Path
                true_start = self._add_node(
                    "THEN", shape="point", width="0.01")
                self.graph.edge(cond_node, true_start,
                                label="T", **self.style["edge"])
                true_end = self._visit_block(stmt.get("then", []), true_start)

                # False Path
                false_start = self._add_node(
                    "ELSE", shape="point", width="0.01")
                self.graph.edge(cond_node, false_start,
                                label="F", **self.style["edge"])
                false_end = self._visit_block(
                    stmt.get("else_", []), false_start)

                # Join
                join_node = self._add_node(
                    "", shape="circle", width="0.1", style="filled", fillcolor="black")

                if true_end:
                    self.graph.edge(true_end, join_node)
                else:
                    self.graph.edge(true_start, join_node)  # Si bloque vacío

                if false_end:
                    self.graph.edge(false_end, join_node)
                else:
                    self.graph.edge(false_start, join_node)  # Si bloque vacío

                current = join_node

            # 3. FOR LOOP
            elif typ == "For":
                var = stmt.get('var')
                start = self._expr_to_str(stmt.get('start'))
                end = self._expr_to_str(stmt.get('end'))

                # Nodo Header
                loop_header = self._add_node(
                    f"FOR {var} 🡨 {start} TO {end}", **self.style["loop"])
                self.graph.edge(current, loop_header, **self.style["edge"])

                # Cuerpo
                body_start = self._add_node("", shape="point", width="0.01")
                self.graph.edge(loop_header, body_start,
                                label="Do", **self.style["edge"])
                body_end = self._visit_block(stmt.get("body", []), body_start)

                # Retorno al ciclo
                if body_end:
                    self.graph.edge(body_end, loop_header, label="Next",
                                    constraint="false", **self.style["edge"])
                else:
                    self.graph.edge(body_start, loop_header, label="Next",
                                    constraint="false", **self.style["edge"])

                # Salida
                exit_node = self._add_node(
                    "", shape="circle", width="0.1", style="filled", fillcolor="black")
                self.graph.edge(loop_header, exit_node,
                                label="Done", **self.style["edge"])
                current = exit_node

            # 4. WHILE LOOP
            elif typ == "While":
                cond = self._expr_to_str(stmt.get('cond'))
                loop_header = self._add_node(
                    f"WHILE {cond}", **self.style["loop"])
                self.graph.edge(current, loop_header, **self.style["edge"])

                body_start = self._add_node("", shape="point", width="0.01")
                self.graph.edge(loop_header, body_start,
                                label="True", **self.style["edge"])
                body_end = self._visit_block(stmt.get("body", []), body_start)

                if body_end:
                    self.graph.edge(body_end, loop_header, label="Loop",
                                    constraint="false", **self.style["edge"])
                else:
                    self.graph.edge(body_start, loop_header, label="Loop",
                                    constraint="false", **self.style["edge"])

                exit_node = self._add_node(
                    "", shape="circle", width="0.1", style="filled", fillcolor="black")
                self.graph.edge(loop_header, exit_node,
                                label="False", **self.style["edge"])
                current = exit_node

            # 5. RETURN
            elif typ == "Return":
                val = self._expr_to_str(stmt.get('value'))
                label = f"RETURN {val}" if val else "RETURN"
                node = self._add_node(
                    label, shape="parallelogram", style="filled", fillcolor="#FFCDD2")
                self.graph.edge(current, node, **self.style["edge"])
                current = node

            # 6. CALL
            elif typ == "Call":
                name = stmt.get('name')
                args = ", ".join([self._expr_to_str(a)
                                 for a in stmt.get('args', [])])
                node = self._add_node(
                    f"CALL {name}({args})", **self.style["call"])
                self.graph.edge(current, node, **self.style["edge"])
                current = node

        return current

    # --- ESTA ES LA FUNCIÓN QUE FALTABA ---
    def _expr_to_str(self, node):
        """Reconstruye una expresión AST a string legible"""
        if not isinstance(node, dict):
            return str(node)

        t = node.get("type")
        if t == "Identifier":
            return node.get("name")
        if t == "LValue":
            return node.get("name")
        if t == "Number":
            return str(node.get("value"))
        if t == "Literal":
            return str(node.get("value"))
        if t == "BinOp":
            op = node.get('op') or "?"
            return f"{self._expr_to_str(node['left'])} {op} {self._expr_to_str(node['right'])}"
        if t == "Unary":
            return f"{node['op']}{self._expr_to_str(node['expr'])}"
        if t == "Call":
            args = ", ".join([self._expr_to_str(a)
                             for a in node.get('args', [])])
            return f"{node.get('name')}({args})"
        if t == "ArrayAccess":
            return f"{node.get('name')}[{self._expr_to_str(node.get('index'))}]"

        return "?"
