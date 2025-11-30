from analyzer.scripts.generate_all_diagrams import ALGORITHMS
from analyzer.gemini_service import GeminiService
from analyzer.complexity_engine import infer_complexity
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.ast_transformer import tree_to_ast
from analyzer.parser import parse_source
import sys
import os

# Configurar path para encontrar los módulos
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '../../'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)


# Importar los algoritmos que ya definiste en los diagramas


def main():
    print("\n🤖 INICIANDO VALIDACIÓN REAL CON GOOGLE GEMINI\n")

    # --- CONFIGURACIÓN DE API KEY ---
    # Puedes poner tu clave aquí directamente entre comillas O usar variable de entorno
    # Ejemplo: api_key = "AIzaSy..."
    api_key = os.environ.get("GOOGLE_API_KEY")

    if not api_key:
        print("❌ ERROR: No se encontró la API Key.")
        print("   Opción A: Define una variable de entorno GOOGLE_API_KEY")
        print("   Opción B: Pégala directamente en el script validate_real.py (línea 23)")
        return

    verifier = GeminiService(api_key=api_key)

    print(f"{'ALGORITMO':<20} | {'MI MOTOR':<15} | {'GEMINI':<15} | {'COINCIDE':<8} | {'TOKENS':<8} | {'TIEMPO'}")
    print("-" * 95)

    results_log = []

    for name, code in ALGORITHMS.items():
        # 1. Análisis Local (Tu Motor)
        try:
            tree = parse_source(code)
            ast = tree_to_ast(tree)
            ctx = analyze_ast_for_patterns(ast)
            local_res = infer_complexity(ctx)

            # Obtener resultado (asumiendo un solo procedimiento)
            proc_data = list(local_res["procedures"].values())[0]
            my_theta = proc_data["big_theta"]

        except Exception as e:
            print(f"Error local en {name}: {e}")
            continue

        # 2. Análisis Remoto (Gemini)
        gemini_res = verifier.verify(code, my_theta)

        if "error" in gemini_res:
            print(f"Error Gemini en {name}: {gemini_res['error']}")
            continue

        analysis = gemini_res["algorithm_analysis"]
        metrics = gemini_res["metrics"]

        match_icon = "✅" if analysis["matches"] else "⚠️"

        # Imprimir fila de tabla
        print(f"{name[:20]:<20} | {my_theta:<15} | {analysis['llm_complexity']:<15} | {match_icon:<8} | {metrics['total_tokens']:<8} | {metrics['latency_ms']}ms")

        results_log.append({
            "name": name,
            "local": my_theta,
            "gemini": analysis['llm_complexity'],
            "match": analysis['matches'],
            "reason": analysis['explanation'],
            "metrics": metrics
        })

    # Guardar reporte detallado
    save_report(results_log)


def save_report(results):
    report_path = os.path.abspath(os.path.join(
        src_path, '../docs/GEMINI_VALIDATION_REPORT.md'))
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 🤖 Reporte de Validación con Google Gemini\n\n")
        f.write("Este documento compara el análisis del motor matemático local contra el modelo Gemini 1.5 Flash.\n")
        f.write(
            "Se incluyen métricas de consumo de tokens y latencia según requerimientos del proyecto.\n\n")

        f.write(
            "| Algoritmo | Mi Motor (Local) | Gemini (IA) | ¿Coinciden? | Tokens Totales | Latencia (ms) |\n")
        f.write("|---|---|---|---|---|---|\n")

        total_tokens = 0
        total_time = 0

        for r in results:
            match = "Sí" if r['match'] else "No"
            m = r['metrics']
            f.write(
                f"| {r['name']} | `{r['local']}` | `{r['gemini']}` | {match} | {m['total_tokens']} | {m['latency_ms']} |\n")
            total_tokens += m['total_tokens']
            total_time += m['latency_ms']

        f.write(f"\n**Totales de la Ejecución:**\n")
        f.write(f"* **Algoritmos Analizados:** {len(results)}\n")
        f.write(f"* **Tokens Consumidos:** {total_tokens}\n")
        f.write(
            f"* **Tiempo Total IA:** {round(total_time/1000, 2)} segundos\n")

    print(f"\n📄 Reporte completo guardado en: {report_path}")


if __name__ == "__main__":
    main()
