import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from analyzer.diagram_generator import TraceGenerator

# Mock AST with an assignment
mock_ast = {
    "procedures": [
        {
            "name": "TestProc",
            "params": [],
            "body": [
                {
                    "type": "Assign",
                    "target": {"type": "Identifier", "name": "x"},
                    "value": {"type": "Number", "value": 1}
                }
            ]
        }
    ]
}

generator = TraceGenerator(mock_ast)
# We want to see the DOT source. 
# The generate() method creates a graphviz.Digraph object.
# We can inspect generator.graph after calling generate() (but generate() renders it).
# Or we can just inspect the _visit_block method logic by running it.

# Let's monkeypatch graphviz.Digraph.render to avoid actual rendering and just print source
import graphviz
original_render = graphviz.Digraph.render

def mock_render(self, filename=None, directory=None, view=False, cleanup=False, format=None, renderer=None, formatter=None, quiet=False, quiet_view=False):
    print("DOT Source:")
    print(self.source)
    return "mock_path"

graphviz.Digraph.render = mock_render

try:
    generator.generate()
except Exception as e:
    print(f"Error: {e}")
