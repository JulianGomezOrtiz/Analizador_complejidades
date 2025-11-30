from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add src to path to import analyzer modules
# Assuming structure: src/server/main.py -> need to go up two levels to reach src parent
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.analyzer.preprocessor import normalize_source
from src.analyzer.parser import parse_source
from src.analyzer.ast_transformer import tree_to_ast
from src.analyzer.static_analyzer import analyze_ast_for_patterns
from src.analyzer.complexity_engine import infer_complexity
from src.analyzer.reporter import format_analysis_json
from src.server.schemas import AnalyzeRequest

app = FastAPI(title="Complexity Analyzer API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
async def analyze_code(request: AnalyzeRequest):
    try:
        norm = normalize_source(request.code)
        tree = parse_source(norm)
        ast = tree_to_ast(tree)
        ctx = analyze_ast_for_patterns(ast)
        
        # If no procedure name provided, pick the first one
        proc_name = request.procedure_name
        if not proc_name:
            if ctx["procedures"]:
                proc_name = list(ctx["procedures"].keys())[0]
            else:
                return {"error": "No procedures found in code", "complexity": None}
        
        if proc_name not in ctx["procedures"]:
             return {"error": f"Procedure '{proc_name}' not found", "complexity": None}

        engine_out = infer_complexity(ctx, proc_name=proc_name)
        
        # Flatten for frontend convenience
        proc_info = engine_out["procedures"][proc_name]
        return {
            "procedure_name": proc_name,
            "complexity": proc_info, 
            "analysis_full": engine_out
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Return error in JSON format instead of 500 for better frontend handling
        return {"error": str(e), "complexity": None}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
