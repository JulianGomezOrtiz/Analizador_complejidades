# 📊 Reporte de Análisis de Complejidad y Patrones

Este documento detalla los patrones algorítmicos detectados automáticamente por el sistema.
Se incluye el análisis de complejidad asintótica y las relaciones de recurrencia.

## Algoritmo: 8_queens
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 7
- Estructura iterativa detectada. Profundidad máxima: 1.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: LCS
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 23
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: binary_search_recursive
**Complejidad Detectada:** `Theta(log n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 10
- Detectadas 2 llamadas recursivas en 'BinarySearch'.
- Forma del Teorema Maestro: T(n) = 2T(n/2) + O(1)
-   -> No hay bucles significativos fuera de la recursión (f(n) = O(1)).
-   -> Aplicando Teorema Maestro (Caso 2 con k=0 para a=1) -> Theta(log n).

**Relación de Recurrencia:** `T(n) = 2T(n/2) + O(1)`

**Cota Fuerte:** `c1*log(n) <= T(n) <= c2*log(n)`

---
## Algoritmo: change_problem
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 7
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: count_pairs
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 7
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Dependencia detectada: El bucle 'j' depende de 'i'.
-   -> Identificado patrón de Serie Aritmética (Triangular).
-   -> Aplicando fórmula de suma: Sum(i) = n(n+1)/2 = Theta(n^2).

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: fibonacci_recursive
**Complejidad Detectada:** `Theta(1.618^n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 6
- Detectadas 2 llamadas recursivas en 'Fibonacci'.
- Recurrencia Lineal Homogénea de Segundo Orden detectada.
-   -> Forma: c1*T(n-1) + c2*T(n-2)
-   -> Ecuación Característica: r^2 - r - 1 = 0
-   -> Raíces: (1 ± sqrt(5)) / 2
-   -> La raíz dominante es Phi (1.618...) -> Crecimiento Exponencial.

**Relación de Recurrencia:** `T(n) = T(n-1) + T(n-2)`

**Cota Fuerte:** `T(n) ~ 1.618^n`

---
## Algoritmo: heap_sort
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 19
- Detectadas 1 llamadas recursivas en 'MaxHeapify'.
- Reducción lineal del problema (T(n-1)).
-   -> Profundidad de la pila de recursión: n
-   -> Costo por nivel: O(1) (sin bucles anidados detectados).

**Relación de Recurrencia:** `T(n) = T(n-1) + c`

**Cota Fuerte:** `T(n) = c*n`

---
## Algoritmo: insertion_sort
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 15
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: knapsack
**Complejidad Detectada:** `Theta(3^n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 15
- Detectadas 3 llamadas recursivas en 'Knapsack'.
- Múltiples llamadas recursivas (3) reduciendo n en 1.
-   -> Forma: T(n) = 3T(n-1) + c
-   -> Profundidad n, ramificación 3 -> Complejidad Exponencial O(3^n).

**Relación de Recurrencia:** `T(n) = 3T(n-1) + c`

**Cota Fuerte:** `T(n) = c*3^n`

---
## Algoritmo: matriz_sum
**Complejidad Detectada:** `Theta(n**2)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 6
- Estructura iterativa detectada. Profundidad máxima: 2.
-   -> Símbolo 'n' no encontrado en límites. Posible O(1) o variable desconocida.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: merge_sort
**Complejidad Detectada:** `Theta(log n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 8
- Detectadas 2 llamadas recursivas en 'MergeSort'.
- Forma del Teorema Maestro: T(n) = 2T(n/2) + O(1)
-   -> No hay bucles significativos fuera de la recursión (f(n) = O(1)).
-   -> Aplicando Teorema Maestro (Caso 2 con k=0 para a=1) -> Theta(log n).

**Relación de Recurrencia:** `T(n) = 2T(n/2) + O(1)`

**Cota Fuerte:** `c1*log(n) <= T(n) <= c2*log(n)`

---
## Algoritmo: quicksort_pivote
**Complejidad Detectada:** `Theta(2^n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 7
- Detectadas 2 llamadas recursivas en 'QuickSort'.
- Múltiples llamadas recursivas (2) reduciendo n en 1.
-   -> Forma: T(n) = 2T(n-1) + c
-   -> Profundidad n, ramificación 2 -> Complejidad Exponencial O(2^n).

**Relación de Recurrencia:** `T(n) = 2T(n-1) + c`

**Cota Fuerte:** `T(n) = c*2^n`

---
## Algoritmo: simple_search
**Complejidad Detectada:** `Theta(n)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 2
- Estructura iterativa detectada. Profundidad máxima: 1.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
## Algoritmo: triple_loop
**Complejidad Detectada:** `Theta(n**3)`

### 🔍 Patrones Identificados:
- Costo base estimado (ops elementales): 6
- Estructura iterativa detectada. Profundidad máxima: 3.
-   -> Límites constantes respecto a 'n' (Serie Geométrica o Constante).
-   -> Producto cartesiano de iteraciones.

**Cota Fuerte:** `c1*g(n) <= T(n) <= c2*g(n)`

---
