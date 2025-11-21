Fase 1 — Especificación y Diseño del Sistema

Analizador de Complejidad Algorítmica a partir de Pseudocódigo\*\*

1. Introducción

Este documento presenta la especificación formal del lenguaje de pseudocódigo, la gramática completa en EBNF, el diseño de arquitectura del sistema, y la definición de interfaces internas correspondientes al proyecto de análisis automático de complejidades para pseudocódigo estructurado.

Esta fase consolida el núcleo conceptual del proyecto, el cual será implementado en fases posteriores. Define:

Sintaxis aceptada (EBNF completa)

Semántica operativa mínima

Diseño arquitectónico modular

Interfaces entre componentes

Modelos de entrada y salida

Criterios de diseño y restricciones

Esta fase no contiene implementación, sino el diseño técnico que guiará el desarrollo del sistema.

2. Objetivo de la Fase

El propósito de esta fase es:

Definir oficialmente el lenguaje de pseudocódigo que el sistema aceptará como entrada.

Formalizar su gramática (EBNF) siguiendo las reglas del enunciado.

Diseñar la arquitectura modular completa del sistema.

Preparar las interfaces internas que permitirán integrar parser, AST, análisis estático y motor de complejidad.

Establecer el formato estándar de entrada y salida, incluyendo:

AST serializable en JSON

análisis paso a paso

resultados finales O, Ω, Θ

Este documento constituye el entregable oficial de la Fase 1.

3. Especificación del lenguaje de pseudocódigo
   3.1 Principios de diseño

El pseudocódigo del proyecto debe:

Ser estructurado, con bloques BEGIN … END.

Separar procedimientos mediante PROCEDURE … END.

Incluir estructuras clásicas de control:
IF, FOR, WHILE, REPEAT, CALL, RETURN.

Permitir arreglos con rangos arbitrarios.

Permitir objetos tipo registro (accesos con .campo).

Permitir expresiones aritméticas y booleanas completas.

Permitir comentarios con ► hasta fin de línea.

Incluir el operador de asignación 🡨 (o := como alternativa).

La sintaxis fue diseñada para representar fielmente lo requerido por el enunciado del curso.

4. Gramática formal (EBNF completa)

Esta es la definición oficial del lenguaje, independientemente del parser Lark.

Se presenta en EBNF legible, estructurada y exhaustiva.

✔ 4.1 EBNF oficial
<start> ::= { <decl_or_proc> }

<decl_or_proc> ::= <var_decl> | <class_decl> | <routine>

<var_decl> ::= "VAR" <var_list> ";"
<var_list> ::= <var_item> { "," <var_item> }
<var_item> ::= IDENTIFIER { "[" <range> "]" }
<range> ::= <expr> [ ".." <expr> ]

<class_decl> ::= "CLASS" IDENTIFIER "{" <class_field_list> "}" ";"
<class_field_list> ::= IDENTIFIER { IDENTIFIER }

<routine> ::= "PROCEDURE" IDENTIFIER "(" [ <param_list> ] ")" <block> "END" ["PROCEDURE"] ";"
<param_list> ::= <param> { "," <param> }

<param> ::= IDENTIFIER [ "[" <range> "]" ] | "Class" IDENTIFIER

<block> ::= "BEGIN" { <statement> } "END"

<statement> ::= <simple_stmt> ";" | <if_stmt> | <while_stmt> | <for_stmt> | <repeat_stmt> | <call_stmt> ";" | <return_stmt> ";"
<simple_stmt> ::= <assign_stmt> | ";"
<assign_stmt> ::= <lvalue> "🡨" <expr>
<lvalue> ::= IDENTIFIER | IDENTIFIER "[" <expr> "]" | IDENTIFIER "." IDENTIFIER

<if_stmt> ::= "IF" "(" <expr> ")" "THEN" <block> [ "ELSE" <block> ] "END"
<while_stmt> ::= "WHILE" "(" <expr> ")" "DO" <block>
<for_stmt> ::= "FOR" IDENTIFIER "🡨" <expr> "TO" <expr> "DO" <block>
<repeat_stmt> ::= "REPEAT" { <statement> } "UNTIL" "(" <expr> ")"

<call_stmt> ::= "CALL" IDENTIFIER "(" [ <arg_list> ] ")"
<arg_list> ::= <expr> { "," <expr> }

<return_stmt> ::= "RETURN" [ <expr> ]

<expr> ::= <or_expr>
<or_expr> ::= <and_expr> { "or" <and_expr> }
<and_expr> ::= <not_expr> { "and" <not_expr> }
<not_expr> ::= "not" <not_expr> | <comparison>
<comparison> ::= <arith> [ ("<" | ">" | "<=" | ">=" | "=" | "<>" | "!=") <arith> ]
<arith> ::= <term> { ("+" | "-") <term> }
<term> ::= <factor> { ("\*" | "/" | "div" | "mod") <factor> }
<factor> ::= "-" <factor> | "+" <factor> | IDENTIFIER "(" [ <arg_list> ] ")" | IDENTIFIER "[" <expr> "]" | IDENTIFIER "." IDENTIFIER | "(" <expr> ")" | NUMBER | STRING | IDENTIFIER | "NULL"

✔ 4.2 Reglas y decisiones de diseño
Asignación

Se acepta 🡨 como símbolo oficial.

Se permite alternativamente := para facilidad de edición.

Comentarios

Proceden del enunciado: ► hasta fin de línea.

El parser debe ignorarlos totalmente.

Arreglos

Índices dinámicos: A[i].

Rangos opcionales: VAR A[1..n][m].

Operadores

Booleanos: and, or, not

Relacionales: <, >, <=, >=, =, <>, !=

Matemáticos: + - \* / div mod

Funciones: ceil(x), floor(x) permitidos como identificadores.

Bloques

Cada IF, FOR, WHILE contiene un <block> obligatorio.

Parámetros

Simples: x, A[1..n]

De clase: Clase Persona

Semántica mínima

El valor del contador de un FOR queda indefinido al finalizar (como en el enunciado).

Evaluación de expresiones es estricta (orden normal).

Llamadas a procedimientos son costosas según análisis.

5. Arquitectura del sistema

El sistema se diseña de forma modular para permitir:

facilidad de pruebas,

extensibilidad,

separación clara entre parser, análisis y motor de complejidad,

integración futura con UI o CLI.

✔ 5.1 Diagrama general de arquitectura
┌────────────────────┐
│ Pseudocódigo RAW │
└──────────┬─────────┘
│ normalize_source()
▼
┌────────────────────┐
│ Preprocessor │
└──────────┬─────────┘
│ parse_source()
▼
┌────────────────────┐
│ Parser │ (Lark)
└──────────┬─────────┘
│ tree_to_ast()
▼
┌────────────────────┐
│ AST Builder │
│ (Transformer) │
└──────────┬─────────┘
│ analyze_ast_for_patterns()
▼
┌────────────────────┐
│ Static Analyzer │
│ loops, rec., calls │
└──────────┬─────────┘
│ infer_complexity()
▼
┌────────────────────┐
│ Complexity Engine │
│ Θ / O / Ω │
└──────────┬─────────┘
│ optional
▼
┌────────────────────┐
│ LLM Verifier │
└──────────┬─────────┘
│ format_analysis_json/text
▼
┌────────────────────┐
│ Output JSON │
│ Output TEXT │
└────────────────────┘

6. Interfaces internas

Esta sección formaliza las funciones y contratos entre módulos.

✔ 6.1 Preprocessor
normalize_source(code: str) -> str

Limpia comentarios

Normaliza operadores

Garantiza entradas válidas al parser

✔ 6.2 Parser
parse_source(code: str) -> lark.Tree

Parsea según la gramática Lark generada a partir de la EBNF.

Devuelve un árbol crudo.

✔ 6.3 AST Transformer
tree_to_ast(tree: Tree) -> Dict

Convierte a un AST JSON serializable.

Cada nodo tiene type y campos relevantes.

✔ 6.4 Static Analyzer
analyze_ast_for_patterns(ast: Dict) -> Dict

Extrae bucles, niveles de anidación, llamadas, recurrencia, etc.

✔ 6.5 Complexity Engine
infer_complexity(context: Dict, proc_name: Optional[str]) -> Dict

Produce:

Big O

Big Theta

Big Omega

Recurrencias

Razonamiento paso a paso

Cotas fuertes

✔ 6.6 LLM Verifier (opcional)
query_llm_for_analysis(code_or_ast: str, prompt: Optional[str], api_key: Optional[str])
→ Dict

✔ 6.7 Reporter
format_analysis_json(ast, engine_output, llm_output) -> Dict
format_analysis_text(engine_output) -> str

7. Formatos de entrada y salida
   ✔ 7.1 Entrada

Texto plano con pseudocódigo que cumple la EBNF.

✔ 7.2 AST (JSON)

Ejemplo:

{
"type": "Program",
"procedures": [
{
"type": "Procedure",
"name": "Fib",
"params": [...],
"body": [...]
}
]
}

✔ 7.3 Salida analizada
{
"analysis": {
"procedures": {
"Fib": {
"big_o": "Theta(phi^n)",
"big_theta": "Theta(phi^n)",
"reasoning": ["Detected recursive pattern n-1 / n-2..."]
}
}
}
}

✔ 7.4 Salida textual
Procedure: Fib
Big-O: Θ(φ^n)
Big-Ω: Θ(φ^n)
Big-Θ: Θ(φ^n)

Reasoning:

- Detected recursive calls...
- Recurrence matches Fibonacci form

8. Conclusión

La Fase 1 define de forma completa:

el lenguaje oficial del proyecto,

su gramática formal,

la arquitectura modular,

interfaces internas,

formato de entrada y salida,

criterios sobre el análisis a realizar.
