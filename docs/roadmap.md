🗺️ Roadmap Maestro: Analizador de Complejidad Algorítmica

Este documento define la hoja de ruta completa para el desarrollo del Sistema de Análisis Automático de Complejidad. El proyecto debe cumplir estrictamente con la gramática Pascal-like especificada y utilizar técnicas avanzadas de análisis matemático (Teorema Maestro, Ecuaciones Características, Sumatorias).

🏁 Fase 0: Preparación y Alcance (Bootstrap)

Objetivo: Alinear el entorno y definir las "Reglas de Oro" del proyecto.

[x] Definición de Sintaxis Estricta:

[x] Asignación obligatoria con 🡨.

[x] Comentarios con ►.

[x] Bloques delimitados por BEGIN ... END.

[x] Semántica del Ciclo FOR:

[x] La variable iteradora retiene su valor al salir del ciclo (Valor límite + Paso).

[x] Definición de Entregables (Ponderación):

[ ] Análisis Formal $O, \Omega, \Theta$ y Cotas Fuertes (60%).

[ ] Diagramas de Seguimiento de Ejecución (15%).

[ ] Técnicas Avanzadas (Árboles, Ec. Característica) (15%).

[ ] Informe Técnico, Pruebas y Recursos (10%).

🏗️ Fase 1: Especificación y Diseño (Core)

Objetivo: Implementar la gramática léxica y sintáctica oficial.

[x] Gramática Formal (EBNF/Lark):

[x] Estructura Global: Clases (definidas antes) + Procedimientos.

[x] Clases y Objetos: Clase Nombre {Atributos} y Clase nombre_instancia.

[x] Estructuras de Control:

FOR ... TO ... DO ...

WHILE ... DO ...

REPEAT ... UNTIL ...

IF ... THEN ... ELSE ...

[x] Vectores: Acceso A[i], Rangos A[1..j], Función intrínseca length(A).

[x] Punteros: Asignación por referencia (y 🡨 x). Soporte para NULL.

[x] Arquitectura de Memoria:

[x] Diferenciar paso por valor (primitivos) vs paso por referencia (objetos/arreglos).

⚙️ Fase 2: Parser y AST

Objetivo: Convertir código fuente en un Árbol de Sintaxis Abstracta robusto.

[x] Implementación del Parser:

[x] Manejo de operadores booleanos short-circuiting (and, or, not).

[x] Operadores matemáticos especiales: div (entera), mod, ┌ ┐ (techo), └ ┘ (piso).

[x] Generación de AST:

[x] Nodos específicos para Call (Llamadas a subrutinas).

[x] Nodos para acceso a campos (x.f) y métodos.

[x] Serialización a JSON para depuración.

🕵️ Fase 3: Análisis Estático y Patrones (🔍 En Curso)

Objetivo: Preparar datos para diagramas y detectar la estrategia de análisis.

[ ] Recorrido del AST (Visitor):

[ ] Implementar TraceGenerator para crear los Diagramas de Seguimiento (Graphviz).

[ ] Identificar anidamientos de bucles y dependencias de variables (ej: j depende de i).

[ ] Contabilizar operaciones elementales por línea (Informe de coste).

[ ] Clasificación Heurística de Algoritmos:

[ ] Divide y Vencerás: Detectar recursión con partición de entrada ($n/2$, $mid$) $\to$ Sugerir Teorema Maestro.

[ ] Recursión Lineal: Detectar $n-k$ $\to$ Sugerir Ecuación Característica.

[ ] Voraz (Greedy): Selección de candidatos en bucle.

[ ] Programación Dinámica: Tablas/Matrices + Bucles anidados dependientes.

🧮 Fase 4: Motor de Complejidad (Razonamiento Formal)

Objetivo: El núcleo matemático. Calcular $T(n)$ y sus cotas asintóticas.

[ ] Motor Iterativo (Sumatorias):

[ ] Convertir bucles FOR en sumatorias $\sum$.

[ ] Resolver series aritméticas ($\sum i$), geométricas ($\sum r^i$) y armónicas ($\sum 1/i$).

[ ] Manejar límites dependientes ($\sum_{i=1}^n \sum_{j=1}^i$).

[ ] Motor Recursivo (Ecuaciones de Recurrencia):

[ ] Generar $T(n)$ automáticamente desde el AST.

[ ] Solver 1: Teorema Maestro. Para formas $T(n) = aT(n/b) + f(n)$.

[ ] Solver 2: Árbol de Recursión. Visualizar niveles y costes por nivel.

[ ] Solver 3: Ecuación Característica (Vital). Para recurrencias lineales homogéneas (ej: Fibonacci $T(n) = T(n-1) + T(n-2)$). Resolver raíces del polinomio ($r^2 - r - 1 = 0$).

[ ] Salida Final: Generar notación $O$ (Peor caso), $\Omega$ (Mejor caso) y $\Theta$ (Caso promedio).

🤖 Fase 5: Validación con LLM

Objetivo: Usar IA como asistente de verificación y parsing flexible.

[ ] Asistencia en Parsing: Usar LLM para traducir lenguaje natural a la gramática estricta (🡨, BEGIN).

[ ] El Juez (Verificación): Enviar el $T(n)$ calculado por el motor y el código al LLM para confirmar concordancia.

[ ] Dataset (Opcional): Usar GPT para generar variaciones de algoritmos para entrenamiento.

🧪 Fase 6: Pruebas y Casos de Prueba (Cobertura)

Objetivo: Validar el sistema con los 10 algoritmos obligatorios.

[ ] Búsqueda Secuencial: Análisis de mejor $O(1)$ y peor caso $O(n)$.

[ ] Insertion Sort: Análisis de bucle while dependiente.

[ ] Triple Loop: Sumatorias anidadas dependientes ($n^3$).

[ ] Merge Sort: Recurrencia $T(n) = 2T(n/2) + n$.

[ ] Quick Sort: Mejor caso ($n \log n$) vs Peor caso ($n^2$).

[ ] Heap Sort / Max Heapify: Análisis estructural sobre árbol.

[ ] Fibonacci (Recursivo): Uso obligatorio de Ecuación Característica ($O(\phi^n)$).

[ ] Problema del Cambio (Voraz): Iterativo con selección.

[ ] N-Reinas (Backtracking): Espacio de búsqueda factorial.

[ ] Problema de la Mochila (Branch & Bound): Poda y cotas.

📝 Fase 7: Informe Técnico y Recursos

Objetivo: Documentación y entregables académicos.

[ ] Informe Técnico:

Metodología utilizada.

Justificación de las técnicas aplicadas.

[ ] Meta-Análisis (Requisito Especial):

Calcular la complejidad asintótica del propio analizador desarrollado (Parser + Motor).

[ ] Recurso Explicativo: Video o animación de la demo funcionando.

📦 Fase 8: Pulido y Entrega Final

Objetivo: Calidad de software y empaquetado.

[ ] Documentación de Código: Docstrings, Type Hints y README robusto.

[ ] Validación Final: Asegurar que la salida incluya razonamiento paso a paso, métricas de coste (microsegundos) y tokens (si aplica).

[ ] Empaquetado: Código modular, limpio y ejecutable mediante scripts sencillos.
