import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from analyzer.preprocessor import normalize_source
from analyzer.parser import parse_source
from analyzer.ast_transformer import tree_to_ast
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.complexity_engine import infer_complexity
from analyzer.reporter import format_analysis_text

def analyze_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()
    
    norm = normalize_source(src)
    try:
        tree = parse_source(norm)
        ast = tree_to_ast(tree)
        ctx = analyze_ast_for_patterns(ast)
        
        # Analyze all procedures
        for proc_name in ctx["procedures"]:
            print(f"--- Analyzing {proc_name} ---")
            engine_out = infer_complexity(ctx, proc_name=proc_name)
            print(format_analysis_text(engine_out))
            print("\n")
            
    except Exception as e:
        print(f"Error analyzing {path}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_file.py <file_path>")
    else:
        analyze_file(sys.argv[1])
