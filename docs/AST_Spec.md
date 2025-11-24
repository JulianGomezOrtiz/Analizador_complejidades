---

#### Paso 2: Documentar la Estructura AST (`docs/AST_SPEC.md`)

Esto es vital para explicar en el informe cómo tu sistema "entiende" el código.

````markdown
# Estructura del Árbol de Sintaxis Abstracta (AST)

El parser transforma el código fuente en una estructura JSON estandarizada.

## Nodos Principales

### Procedure

Representa una función o subrutina.

```json
{
  "type": "Procedure",
  "name": "BinarySearch",
  "params": [{"name": "A", "param_type": "any"}, ...],
  "body": [...] // Lista de sentencias
}
For Loop
Representa un ciclo determinista.

JSON

{
  "type": "For",
  "var": "i",
  "start": {"type": "Number", "value": 1},
  "end": {"type": "Identifier", "name": "n"},
  "body": [...]
}
Assign
Representa la mutación de estado (🡨).

JSON

{
  "type": "Assign",
  "target": {"type": "LValue", "name": "x"},
  "value": {"type": "BinOp", "op": "+", ...}
}
```
````
