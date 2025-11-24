import graphviz
from typing import Dict, Any


class TraceGenerator:
    """
    Genera un Diagrama de Flujo de Control (CFG) visual a partir del AST.
    Utiliza Graphviz para renderizar la imagen.
    """

    def __init__(self, ast: Dict[str, Any], output_format='png'):
        self.ast = ast
        self.format = output_format
        self.graph = None
        self.node_count = 0

    def generate(self, filename='trace_output'):
        """
        Punto de entrada principal. Genera un diagrama por cada procedimiento.
        """
        procs = self.ast.get("procedures", [])

        for proc in procs:
            proc_name = proc.get("name", "Unknown")
            # Crear un nuevo grafo para cada procedimiento
            self.graph = graphviz.Digraph(
                f'cluster_{proc_name}', format=self.format)
            self.graph.attr(label=f'Diagrama de Seguimiento: {proc_name}')
            self.node_count = 0

            # Nodo Inicial
            start_node = self._add_node(
                "START", shape="oval", style="filled", fillcolor="lightgreen")

            # Recorrer el cuerpo
            last_node = self._visit_block(proc.get("body", []), start_node)

            # Nodo Final
            end_node = self._add_node(
                "END", shape="oval", style="filled", fillcolor="lightcoral")
            if last_node:
                self.graph.edge(last_node, end_node)

            # Renderizar
            output_path = f"docs/diagrams/{proc_name}_trace"
            self.graph.render(output_path, cleanup=True)
            print(f"✅ Diagrama generado: {output_path}.{self.format}")

    def _add_node(self, label, shape="box", style="", fillcolor=""):
        node_id = f"node_{self.node_count}"
        self.node_count += 1
        self.graph.node(node_id, label=label, shape=shape,
                        style=style, fillcolor=fillcolor)
        return node_id

    def _visit_block(self, stmts, previous_node):
        current_prev = previous_node

        for stmt in stmts:
            typ = stmt.get("type")

            if typ == "Assign":
                target = stmt["target"]["name"]
                # Simplificación visual del valor
                label = f"{target} 🡨 ..."
                node = self._add_node(label)
                self.graph.edge(current_prev, node)
                current_prev = node

            elif typ == "If":
                # Nodo de decisión (Rombo)
                cond_node = self._add_node(
                    "¿Condición?", shape="diamond", style="filled", fillcolor="lightyellow")
                self.graph.edge(current_prev, cond_node)

                # Rama TRUE
                true_start = self._add_node("THEN", shape="point")
                self.graph.edge(cond_node, true_start, label="True")
                true_end = self._visit_block(stmt.get("then", []), true_start)

                # Rama FALSE
                false_start = self._add_node("ELSE", shape="point")
                self.graph.edge(cond_node, false_start, label="False")
                false_end = self._visit_block(
                    stmt.get("else_", []), false_start)

                # Nodo de convergencia
                join_node = self._add_node("", shape="circle", width="0.1")
                if true_end:
                    self.graph.edge(true_end, join_node)
                if false_end:
                    self.graph.edge(false_end, join_node)

                current_prev = join_node

            elif typ == "For":
                # Inicio del ciclo
                var = stmt.get("var")
                loop_cond = self._add_node(
                    f"FOR {var}", shape="hexagon", style="filled", fillcolor="lightblue")
                self.graph.edge(current_prev, loop_cond)

                # Cuerpo del ciclo
                body_start = self._add_node("DO", shape="point")
                self.graph.edge(loop_cond, body_start, label="Iterate")
                body_end = self._visit_block(stmt.get("body", []), body_start)

                # Vuelta al inicio (Loop back)
                if body_end:
                    self.graph.edge(body_end, loop_cond,
                                    constraint="false")  # Back edge

                # Salida del ciclo
                loop_exit = self._add_node("Exit Loop", shape="point")
                self.graph.edge(loop_cond, loop_exit, label="Finish")
                current_prev = loop_exit

            elif typ == "Call":
                name = stmt.get("name")
                node = self._add_node(f"CALL {name}", shape="component")
                self.graph.edge(current_prev, node)
                current_prev = node

            elif typ == "Return":
                node = self._add_node(
                    "RETURN", shape="parallelogram", style="filled", fillcolor="lightgrey")
                self.graph.edge(current_prev, node)
                current_prev = node

        return current_prev
