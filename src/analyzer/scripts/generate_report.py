import sys
import os

# Configuración de path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.abspath(os.path.join(current_dir, '../../'))
if src_path not in sys.path:
    sys.path.insert(0, src_path)

from analyzer.complexity_engine import infer_complexity
from analyzer.static_analyzer import analyze_ast_for_patterns
from analyzer.ast_transformer import tree_to_ast
from analyzer.parser import parse_source


def main():
    print("📝 Generando Reporte de Análisis de Patrones (En Español)...")

    # Definir rutas
    report_path = os.path.abspath(os.path.join(
        src_path, '../docs/ANALYSIS_REPORT.md'))
    examples_path = os.path.abspath(os.path.join(src_path, '../examples'))

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 Reporte de Análisis de Complejidad y Patrones\n\n")
        f.write(
            "Este documento detalla los patrones algorítmicos detectados automáticamente por el sistema.\n")
        f.write(
            "Se incluye el análisis de complejidad asintótica y las relaciones de recurrencia.\n\n")

        # Iterar sobre archivos en la carpeta examples
        if not os.path.exists(examples_path):
            print(f"❌ No se encontró la carpeta de ejemplos: {examples_path}")
            return

        files = [f for f in os.listdir(examples_path) if f.endswith('.pseudo')]
        files.sort()  # Ordenar para consistencia

        for filename in files:
            name = os.path.splitext(filename)[0]
            file_path = os.path.join(examples_path, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as alg_file:
                    code = alg_file.read()

                # 1. Pipeline de Análisis
                tree = parse_source(code)
                ast = tree_to_ast(tree)
                ctx = analyze_ast_for_patterns(ast)
                complexity = infer_complexity(ctx, proc_name=None)

                # Extraer datos del procedimiento principal
                # Si hay múltiples, tomamos el primero o iteramos (asumimos uno principal por archivo por ahora)
                if not complexity["procedures"]:
                     f.write(f"## Algoritmo: {name}\n")
                     f.write("No se detectaron procedimientos.\n\n---\n")
                     continue

                proc_data = list(complexity["procedures"].values())[0]

                f.write(f"## Algoritmo: {name}\n")
                f.write(
                    f"**Complejidad Detectada:** `{proc_data['big_theta']}`\n\n")

                f.write("### 🔍 Patrones Identificados:\n")
                for reason in proc_data['reasoning']:
                    f.write(f"- {reason}\n")

                if proc_data.get('recurrence'):
                    f.write(
                        f"\n**Relación de Recurrencia:** `{proc_data['recurrence']}`\n")

                f.write(f"\n**Cota Fuerte:** `{proc_data['cotas_fuertes']}`\n")
                f.write("\n---\n")

                print(f"✅ Analizado: {name}")

            except Exception as e:
                print(f"❌ Error en {name}: {e}")
                f.write(f"## {name}\nERROR: {e}\n\n---\n")

    print(f"\n📄 Reporte guardado en: {report_path}")


if __name__ == "__main__":
    main()
