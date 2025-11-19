# src/analyzer/llm_verifier.py
"""
Módulo opcional para consultar un LLM para verificación.
Implementación segura: no incluye dependencias concretas; usa requests to OpenAI-like endpoints
si el usuario provee una API key vía variables de entorno y la función la recibe.

Notas de seguridad:
 - NUNCA debes subir API keys al repo.
 - Al ejecutar en CI, configura secrets.OPENAI_API_KEY en GitHub.
"""
from typing import Dict, Any, Optional
import os
import json

# Esta implementación es un "adapter" que puedes extender según la API del proveedor.
# Aquí devolvemos un stub si no hay api_key para no romper el flujo.


def query_llm_for_analysis(code_or_ast: str, prompt: Optional[str] = None, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Llama al LLM y pide un análisis de complejidad.
    Si api_key es None -> devuelve un stub con consejo y sin contactar la API.

    Args:
      code_or_ast: cadena con el pseudocódigo o el AST JSON
      prompt: prompt adicional (opcional)
      api_key: clave para la API; si None devuelve stub.

    Returns:
      dict con: { "suggested_complexity": { "O":..., "Omega":..., "Theta":... }, "analysis_text": "..."}
    """
    if not api_key:
        # stub - útil para tests locales sin clave
        return {
            "analysis_text": "LLM not called (no api_key provided). This is a local stub.",
            "suggested_complexity": {"O": None, "Omega": None, "Theta": None},
            "notes": "Provide OPENAI_API_KEY to enable LLM verification."
        }

    # Example placeholder: user can implement actual HTTP call here to OpenAI/Gemini.
    # For safety we don't ship a concrete API client here (to avoid accidental credentials leak).
    # Provide a clear template for how to implement:
    template = {
        "analysis_text": "LLM call not implemented in this adapter. Implement provider specific call.",
        "suggested_complexity": {"O": None, "Omega": None, "Theta": None},
        "notes": "Implement API call in llm_verifier.query_llm_for_analysis using your provider."
    }
    return template
