README.md (versión final, profesional y simple)

# Analizador de Complejidades

Proyecto desarrollado para la asignatura Análisis y Diseño de Algoritmos.  
El objetivo es recibir pseudocódigo como entrada, procesarlo mediante un preprocesador, generar un AST, aplicar análisis estático para identificar patrones (bucles, recursión, divide and conquer, programación dinámica, etc.) y calcular la complejidad asintótica del algoritmo en notación O, Ω y Θ.

---

## Estructura del proyecto

analizador_complejidades/
│
├── src/
│ └── analyzer/
│ ├── preprocessor.py
│ ├── parser.py
│ ├── grammar.lark
│ ├── ast_transformer.py
│ ├── static_analyzer.py
│ ├── complexity_engine.py
│ ├── llm_verifier.py
│ └── reporter.py
│
├── examples/
│ (10 algoritmos base utilizados para pruebas)
│
├── tests/
│ (pruebas unitarias e integración)
│
├── docs/
│ ├── especificacion_gramatica.md
│ ├── design.md
│ └── roadmap.md
│
├── requirements.txt
├── .gitignore
└── README.md

---

## Requisitos

- Python 3.10 o superior
- pip actualizado
- Dependencias descritas en `requirements.txt`:

lark==1.2.2
pytest==8.2.1
typing_extensions>=4.0.0

Las dependencias se instalan automáticamente mediante:

pip install -r requirements.txt

---

## Instrucciones para desarrollo local

```bash
# Clonar el repositorio
git clone git@github.com:JulianGomezOrtiz/analizador-complejidades.git
cd analizador-complejidades

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar pruebas
pytest -q

Pruebas:
La carpeta tests/ contiene pruebas para:

Preprocesador
Parser
Transformación del AST
Análisis estático
Motor de complejidad
Pipeline completo
Validación con los 10 ejemplos base
Estas pruebas permiten verificar el correcto comportamiento del sistema en cada fase.

Documentación:
El directorio docs/ incluye:

especificacion_gramatica.md: gramática formal del pseudocódigo en EBNF.
design.md: arquitectura interna del sistema.
roadmap.md: plan de trabajo estructurado por fases.


Información
Proyecto académico elaborado para la materia Análisis y Diseño de Algoritmos.
Autor: Julián Gómez Ortiz
```
