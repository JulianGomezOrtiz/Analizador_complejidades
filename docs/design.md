flowchart LR
U[CLI / UI] --> P[Preprocessor]
P --> PARSER[Lark Parser]
PARSER --> ASTT[AST Transformer]
ASTT --> STATIC[Static Analyzer]
STATIC --> ENGINE[Complexity Engine]
ENGINE --> REPORT[Reporter / Formatter]
ENGINE --> LLM[LLM Verifier]
LLM --> ENGINE
REPORT --> U
TESTS[Tests (pytest)] --> PARSER
TESTS --> ASTT
TESTS --> ENGINE
subgraph infra
REPO[GitHub Repo]
CI[GitHub Actions]
end
REPO --> CI
CI --> TESTS
