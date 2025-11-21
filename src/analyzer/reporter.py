# src/analyzer/reporter.py
"""
Formatea la salida final: AST JSON + analysis JSON + readable text.
"""
from typing import Dict, Any
import json
from datetime import datetime


def generate_report(data):
    return "Reporte generado correctamente."


def format_analysis_json(ast: Dict[str, Any], engine_output: Dict[str, Any], llm_output: Dict[str, Any] = None) -> Dict[str, Any]:
    meta = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "parser_version": "grammar_v1",
    }
    return {
        "meta": meta,
        "ast": ast,
        "analysis": engine_output,
        "llm": llm_output or {},
    }


def format_analysis_text(engine_output: Dict[str, Any]) -> str:
    """
    Produce un texto con razonamiento paso a paso para el usuario.
    engine_output is expected to have engine_output['procedures'][name]['reasoning'] etc.
    """
    lines = []
    procs = engine_output.get("procedures", {})
    for name, info in procs.items():
        lines.append(f"Procedure: {name}")
        lines.append("-" * (9 + len(name)))
        lines.append(f"Big-O : {info.get('big_o')}")
        lines.append(f"Big-Ω : {info.get('big_omega')}")
        lines.append(f"Big-Θ : {info.get('big_theta')}")
        if info.get("recurrence"):
            lines.append(f"Recurrence: {info.get('recurrence')}")
        lines.append("Reasoning:")
        for step in info.get("reasoning", []):
            lines.append(f"  - {step}")
        lines.append("")  # blank line between procs
    return "\n".join(lines)
