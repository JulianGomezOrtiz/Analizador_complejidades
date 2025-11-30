# 📊 Reporte de Análisis de Complejidad y Patrones

Este documento detalla los patrones algorítmicos detectados automáticamente por el sistema.
Se incluye el análisis de complejidad asintótica y las relaciones de recurrencia.

## Algoritmo: 1_LinearSearch
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 1.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*n^1 <= T(n) <= c2*n^1`

---
## Algoritmo: 2_MatrixSum
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*n^2 <= T(n) <= c2*n^2`

---
## Algoritmo: 3_BinarySearch
**Complejidad Detectada:** `Theta(log n)`

### 🔍 Patrones Identificados:
- Detectadas 2 llamadas recursivas en 'BinarySearch'.
- Forma del Teorema Maestro: T(n) = 2T(n/2) + O(1)
-   -> No hay bucles significativos fuera de la recursión (f(n) = O(1)).
-   -> Aplicando Teorema Maestro (Caso 2 con k=0 para a=1) -> Theta(log n).

**Relación de Recurrencia:** `T(n) = 2T(n/2) + O(1)`

**Cota Fuerte:** `c1*log(n) <= T(n) <= c2*log(n)`

---
## Algoritmo: 4_MergeSort
**Complejidad Detectada:** `Theta(n log n)`

### 🔍 Patrones Identificados:
- Detectadas 2 llamadas recursivas en 'MergeSort'.
- Forma del Teorema Maestro: T(n) = aT(n/b) + f(n)
-   -> a = 2 (llamadas), b = 2 (división)
-   -> f(n) es O(n) debido a bucles presentes (Merge/Partition).
-   -> log_b(a) = log_2(2) = 1
-   -> Caso 2: f(n) es Theta(n^log_b a) * log^k n -> Resultado Theta(n log n)

**Relación de Recurrencia:** `T(n) = 2T(n/2) + O(n)`

**Cota Fuerte:** `c1*n*log(n) <= T(n) <= c2*n*log(n)`

---
## Algoritmo: 5_Fibonacci
**Complejidad Detectada:** `Theta(phi^n)`

### 🔍 Patrones Identificados:
- Detectadas 2 llamadas recursivas en 'Fib'.
- Recurrencia Lineal Homogénea de Segundo Orden detectada.
-   -> Forma: c1*T(n-1) + c2*T(n-2)
-   -> Ecuación Característica: r^2 - r - 1 = 0
-   -> Raíces: (1 ± sqrt(5)) / 2
-   -> La raíz dominante es Phi (1.618...) -> Crecimiento Exponencial.

**Relación de Recurrencia:** `T(n) = T(n-1) + T(n-2)`

**Cota Fuerte:** `T(n) ~ 1.618^n`

---
## Algoritmo: 6_TripleLoop
**Complejidad Detectada:** `Theta(n**3)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 3.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*n^3 <= T(n) <= c2*n^3`

---
## Algoritmo: 7_QuickSort
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Detectadas 2 llamadas recursivas en 'QuickSort'.
- Reducción lineal del problema (T(n-1)).
-   -> Profundidad de la pila de recursión: n
-   -> Costo por nivel: O(1) (sin bucles anidados detectados).

**Relación de Recurrencia:** `T(n) = T(n-1) + c`

**Cota Fuerte:** `T(n) = c*n`

---
## Algoritmo: 8_LCS_Dynamic
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*n^2 <= T(n) <= c2*n^2`

---
## Algoritmo: 9_NQueens
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 1.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*n^1 <= T(n) <= c2*n^1`

---
## Algoritmo: 10_CountPairs
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Dependencia detectada: El bucle 'j' depende de 'i'.
-   -> Identificado patrón de Serie Aritmética (Triangular).
-   -> Aplicando fórmula de suma: Sum(i) = n(n+1)/2 = Theta(n^2).

**Cota Fuerte:** `c1*n^2 <= T(n) <= c2*n^2`

---
