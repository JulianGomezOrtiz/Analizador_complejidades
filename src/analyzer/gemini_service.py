import os
import time
import json
import google.generativeai as genai
from typing import Dict, Any


class GeminiVerifier:
    """
    Cliente para validación de complejidad usando Google Gemini.
    Selecciona automáticamente el mejor modelo disponible.
    """

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self.model = None

        if not self.api_key:
            print("⚠️ ADVERTENCIA: No se encontró GOOGLE_API_KEY.")
            return

        genai.configure(api_key=self.api_key)
        self.model = self._select_best_model()

    def _select_best_model(self):
        """Busca un modelo disponible compatible con generateContent."""
        try:
            # Lista de preferencias en orden
            preferences = ["gemini-1.5-flash", "gemini-1.5-pro",
                           "gemini-pro", "gemini-1.0-pro"]

            available = [m.name for m in genai.list_models(
            ) if 'generateContent' in m.supported_generation_methods]

            # 1. Buscar coincidencia exacta de preferencias
            for pref in preferences:
                # La API devuelve nombres como 'models/gemini-pro', así que buscamos si termina en nuestra preferencia
                match = next((m for m in available if m.endswith(pref)), None)
                if match:
                    print(f"   ✅ Modelo seleccionado: {match}")
                    return genai.GenerativeModel(match)

            # 2. Si no, tomar el primero disponible
            if available:
                print(
                    f"   ⚠️ Modelos preferidos no hallados. Usando fallback: {available[0]}")
                return genai.GenerativeModel(available[0])

        except Exception as e:
            print(
                f"   ❌ Error listando modelos: {e}. Intentando default 'gemini-pro'...")
            return genai.GenerativeModel('gemini-pro')

        print("   ❌ No se encontraron modelos compatibles.")
        return None

    def verify(self, algorithm_code: str, student_complexity: str) -> Dict[str, Any]:
        if not self.model:
            return {"error": "No hay modelo disponible", "matches": False, "metrics": {"latency_ms": 0, "total_tokens": 0}}

        prompt = f"""
        Actúa como experto en algoritmos. Analiza este pseudocódigo (Pascal-like):
        ```
        {algorithm_code}
        ```
        Calcula la complejidad Theta. Compárala con: "{student_complexity}".
        Responde SOLO JSON:
        {{ "llm_complexity": "Theta(...)", "matches": true/false, "explanation": "..." }}
        """

        start_time = time.perf_counter()

        try:
            response = self.model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )

            end_time = time.perf_counter()
            latency_ms = (end_time - start_time) * 1000

            # Métricas
            try:
                usage = response.usage_metadata
                total_tokens = usage.total_token_count
            except:
                total_tokens = 0  # Fallback si la API no envía datos

            # Parsear JSON
            try:
                result_json = json.loads(response.text)
            except:
                # Intento de limpieza si devuelve Markdown
                text = response.text.replace(
                    "```json", "").replace("```", "").strip()
                try:
                    result_json = json.loads(text)
                except:
                    result_json = {"llm_complexity": "Error Formato",
                                   "matches": False, "explanation": "Respuesta no JSON"}

            return {
                "algorithm_analysis": result_json,
                "metrics": {
                    "latency_ms": round(latency_ms, 2),
                    "total_tokens": total_tokens
                }
            }

        except Exception as e:
            return {
                "error": str(e),
                "matches": False,
                "metrics": {"latency_ms": 0, "total_tokens": 0}
            }
