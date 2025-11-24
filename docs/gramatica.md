# Especificación Gramatical del Analizador de Complejidades

Este sistema implementa un parser para un lenguaje imperativo estilo Pascal, cumpliendo estrictamente con las convenciones del proyecto.

## 1. Convenciones Léxicas

- **Asignación:** Se utiliza el símbolo Unicode `🡨` (U+1F868).
- **Comentarios:** Inician con `►` (U+25BA) e ignoran el resto de la línea.
- **Identificadores:** Alfanuméricos comenzando con letra (`[a-zA-Z_][a-zA-Z0-9_]*`).
- **Números:** Enteros y flotantes.

## 2. Estructura del Programa

Un programa consta de una sección opcional de definición de clases seguida de una o más subrutinas.

```ebnf
program ::= class_decl* procedure+
3. Definición de Datos
Clases: Se definen antes de los procedimientos. Clase <Nombre> { <Atributo1> <Atributo2> ... }

Objetos: Se declaran explícitamente. Clase <nombre_instancia>;

Arreglos: Acceso mediante corchetes, soportando rangos. A[i] o A[1..n]

4. Estructuras de Control
Bloques: Delimitados por BEGIN y END.

Condicional: IF <cond> THEN <bloque> [ELSE <bloque>]

Ciclo FOR: FOR <var> 🡨 <inicio> TO <fin> DO <bloque>

Nota: La variable retiene su valor al salir del ciclo.

Ciclo WHILE: WHILE <cond> DO <bloque>

Ciclo REPEAT: REPEAT <sentencias> UNTIL <cond>

5. Operadores Soportados
Aritméticos: +, -, *, /, div, mod, ┌ ┐ (techo), └ ┘ (piso).

Lógicos: and, or, not (Short-circuiting).

Relacionales: <, >, <=, >=, =, ≠ (o <>).

6. Recursión y Procedimientos
Llamadas mediante CALL <nombre>(<args>) o como expresión en asignaciones.

Retorno de valores mediante RETURN <valor>.
```
