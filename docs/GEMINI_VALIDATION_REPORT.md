# 🤖 Reporte de Validación con Google Gemini

Este documento compara el análisis del motor matemático local contra el modelo Gemini 1.5 Flash.
Se incluyen métricas de consumo de tokens y latencia según requerimientos del proyecto.

| Algoritmo | Mi Motor (Local) | Gemini (IA) | ¿Coinciden? | Tokens Totales | Latencia (ms) |
|---|---|---|---|---|---|
| 1_LinearSearch | `Theta(n)` | `Theta(n)` | Sí | 1329 | 12670.31 |
| 2_MatrixSum | `Theta(n**2)` | `Theta(n^2)` | Sí | 1233 | 9940.39 |
| 3_BinarySearch | `Theta(log n)` | `Theta(log n)` | Sí | 1330 | 10073.78 |
| 4_MergeSort | `Theta(n log n)` | `Theta(n log n)` | Sí | 1737 | 13193.2 |
| 5_Fibonacci | `Theta(phi^n)` | `Theta(phi^n)` | Sí | 1399 | 11637.51 |
| 6_TripleLoop | `Theta(n**3)` | `Theta(n^3)` | Sí | 1348 | 11266.9 |
| 7_QuickSort | `Theta(n)` | `Theta(n log n)` | No | 1362 | 11150.02 |
| 8_LCS_Dynamic | `Theta(n**2)` | `Theta(m*n)` | Sí | 1855 | 14331.21 |
| 9_NQueens | `Theta(n)` | `Theta(n!)` | No | 1967 | 16708.91 |
| 10_CountPairs | `Theta(n**2)` | `Theta(n^2)` | Sí | 1476 | 11238.37 |

**Totales de la Ejecución:**
* **Algoritmos Analizados:** 10
* **Tokens Consumidos:** 15036
* **Tiempo Total IA:** 122.21 segundos
