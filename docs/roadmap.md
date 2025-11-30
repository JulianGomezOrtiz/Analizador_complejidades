Tienes toda la razón. Al intentar sintetizar, agrupé algunas etapas finales, pero para un proyecto de esta envergadura es mejor mantener la **granularidad** de tu plan original (Fases 0 a 8), ya que te permite un control más fino del avance.

Aquí tienes el **Roadmap Completo (Fases 0 a 8)**, respetando tu estructura original pero **inyectando** en cada fase los requisitos técnicos exactos extraídos de los documentos `Proyecto_Gramatica` y `ADA_24A___Notas`.

---

### 🗺️ Roadmap Maestro Detallado: Analizador de Complejidades

#### Fase 0 — Preparación y Alcance (Bootstrap)

_Objetivo: Alinear el entorno con las reglas estrictas del enunciado._

- **Leer y fijar alcance obligatorio:**
  - [cite_start]Confirmar soporte para caracteres especiales: asignación `🡨` [cite: 46] [cite_start]y comentarios `►`[cite: 45].
  - [cite_start]Entender la diferencia en el ciclo `FOR`: la variable iteradora **retiene su valor** al salir del ciclo (valor límite + paso)[cite: 5, 6]. Esto afecta el análisis de seguimiento.
- **Decidir entregables:**
  - [cite_start]Análisis O, Ω, Θ y cotas fuertes (60%)[cite: 88, 114].
  - [cite_start]Diagramas de seguimiento (15%)[cite: 114].
  - [cite_start]Técnicas avanzadas (Árboles, Teorema Maestro, Ecuación característica) (15%)[cite: 114].
- **Selección de herramientas:** Python (recomendado) + ANTLR/Lark.

#### Fase 1 — Especificación y Diseño (Core)

_Objetivo: Definir la estructura sintáctica tal cual la pide el documento._

- **Definir Gramática (BNF/EBNF):**
  - [cite_start]**Estructuras de control:** `for ... to ... do`, `while ... do`, `repeat ... until`, `if ... then ... else`[cite: 7, 15, 23, 30].
  - [cite_start]**Clases y Objetos:** Las clases se definen **antes** del algoritmo (`Clase Nombre {Atributos}`)[cite: 55]. [cite_start]Los objetos se instancian al inicio del algoritmo (`Clase nombre_objeto`)[cite: 57].
  - [cite_start]**Vectores:** Acceso con `A[i]`, rangos `A[1..j]` y función `length(A)`[cite: 49, 50, 52].
  - **Punteros:** Variables de objetos/arreglos actúan como punteros. [cite_start]`y 🡨 x` hace que apunten a lo mismo[cite: 60, 61]. [cite_start]Soporte para valor `NULL`[cite: 63].
- **Diseño de Arquitectura:**
  - [cite_start]El módulo de análisis debe separar memoria de "variables primitivas" (paso por valor) y "objetos" (paso por referencia, aunque los campos sí son mutables)[cite: 64, 65].

#### Fase 2 — Parser y Representación Intermedia

_Objetivo: Convertir texto en AST manejando las excentricidades de la gramática._

- **Implementar Parser:**
  - [cite_start]Manejar operadores booleanos _short-circuiting_ (`and`, `or`, `not`)[cite: 81].
  - [cite_start]Manejar operadores matemáticos incluyendo `div` (división entera), `mod`, `┌ ┐` (techo), `└ ┘` (piso)[cite: 86].
- **Generar AST:**
  - [cite_start]El AST debe tener nodos específicos para `Call` (llamada a subrutina)[cite: 80].
  - [cite_start]Nodos para acceso a campos de objetos `x.f`[cite: 58].

#### Fase 3 — Análisis Estático y Patrones

_Objetivo: Preparar los datos para el diagrama de seguimiento y detectar el tipo de algoritmo._

- **Recorrido del AST:**
  - [cite_start]Identificar anidamientos para diagramas de seguimiento (Trace)[cite: 105].
  - [cite_start]Contabilizar operaciones elementales por línea para el informe de "coste por instrucción"[cite: 106].
- **Clasificación de Patrones (Heurística):**
  - [cite_start]Detectar **Divide y Vencerás** (Recursión con partición de entrada) -> Sugerir Teorema Maestro/Árbol[cite: 643].
  - [cite_start]Detectar **Recursión Lineal** -> Sugerir Ecuación Característica[cite: 1002].
  - [cite_start]Detectar **Voraz/Greedy** (Selección de candidatos en bucle)[cite: 1053].
  - [cite_start]Detectar **Programación Dinámica** (Tablas/Matrices + Bucles anidados dependientes)[cite: 1397].

#### Fase 4 — Motor de Complejidad (Razonamiento Formal)

_Objetivo: El núcleo matemático (60% de la nota)._

- **Motor para Iterativos:**
  - Convertir bucles en sumatorias. [cite_start]Reconocer series aritméticas ($\sum i$) [cite: 556][cite_start], geométricas ($\sum r^i$) [cite: 561][cite_start], y armónicas ($\sum 1/i$)[cite: 580].
- **Motor para Recursivos:**
  - Generar $T(n)$ automáticamente.
  - [cite_start]**Solver 1: Teorema Maestro.** Para formas $T(n) = aT(n/b) + f(n)$[cite: 956].
  - [cite_start]**Solver 2: Árbol de Recursión.** Para visualizar niveles y costes[cite: 927].
  - [cite_start]**Solver 3: Ecuación Característica.** **(Vital)** Para recurrencias lineales homogéneas (tipo Fibonacci $T(n) = T(n-1) + T(n-2)$) resolver raíces del polinomio característico[cite: 1004, 1013].
- **Salida:**
  - [cite_start]Producir notación $O$ (Peor caso), $\Omega$ (Mejor caso) y $\Theta$ (Caso promedio)[cite: 2].

#### Fase 5 — Validación y Verificación con LLM

_Objetivo: Usar IA como asistente y juez, no como creador único._

- [cite_start]**Asistencia en Parsing:** Usar LLM para sugerir la estructura lógica si el pseudocódigo es ambiguo[cite: 119].
- [cite_start]**Comparación de Resultados:** Enviar tu $T(n)$ calculado y el del LLM para ver concordancia[cite: 120].
- [cite_start]**Entrenamiento (Opcional/Crédito extra):** Usar GPT para generar dataset de algoritmos y clasificar estructuras[cite: 121].

#### Fase 6 — Pruebas y Casos de Prueba (Cobertura)

_Objetivo: Batería de 10 algoritmos obligatorios basados en las notas._

1.  [cite_start]**Búsqueda Secuencial:** Análisis de mejor ($O(1)$) y peor caso ($O(n)$)[cite: 423, 431, 462].
2.  [cite_start]**Insertion Sort:** Análisis de bucle `while` dependiente[cite: 487].
3.  [cite_start]**Triple Loop:** Sumatorias anidadas dependientes[cite: 512].
4.  [cite_start]**Merge Sort:** Recurrencia $2T(n/2) + n$[cite: 677].
5.  [cite_start]**Quick Sort:** Mejor caso ($n \log n$) vs Peor caso ($n^2$)[cite: 681, 694].
6.  [cite_start]**Heap Sort / Max Heapify:** Análisis estructural sobre árbol[cite: 776].
7.  [cite_start]**Fibonacci (Recursivo):** Uso de ecuación característica[cite: 1013].
8.  [cite_start]**Problema del Cambio (Voraz):** Iterativo[cite: 1055].
9.  [cite_start]**N-Reinas (Backtracking):** Espacio de búsqueda factorial[cite: 1101].
10. [cite_start]**Problema de la Mochila (Branch & Bound):** Poda y cotas[cite: 1220].

#### Fase 7 — Informe Técnico y Recursos

_Objetivo: Entregables de documentación._

- **Informe:** Metodología, técnicas aplicadas.
- [cite_start]**Análisis del Propio Analizador:** Debes calcular la complejidad asintótica de tu propio sistema (Parser + Motor)[cite: 109].
- [cite_start]**Recurso Explicativo:** Video o animación de la demo[cite: 112].

#### Fase 8 — Pulido y Entrega Final

_Objetivo: Empaquetado y calidad._

- **Documentación:** Docstrings y README.
- [cite_start]**Validación Final:** Asegurar que la salida incluya razonamiento paso a paso (microsegundos y tokens por llamado si usas API)[cite: 106].
- [cite_start]**Empaquetado:** Código modularizado y funcional[cite: 110].

---

Este roadmap ahora incluye las **8 fases** y no olvida ningún detalle de los adjuntos, especialmente los métodos matemáticos de las notas (Fase 4) y las reglas gramaticales específicas (Fase 1). ¿Te parece que ahora sí refleja la totalidad de tu plan?
