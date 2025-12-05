from lark import Lark, Transformer, v_args

grammar = """
    start: stmt+
    stmt: "var" NAME "=" NUMBER
    NAME: /[a-z]+/
    NUMBER: /\d+/
    %import common.WS
    %ignore WS
"""

parser = Lark(grammar, propagate_positions=True)

class TestTransformer(Transformer):
    def NAME(self, token):
        return {"type": "id", "value": str(token), "line": token.line}
    
    def stmt(self, items):
        # items[0] is "var" (Token if terminal? No, "var" is anonymous terminal)
        # items[1] is NAME dict
        return {"type": "stmt", "line": items[1]["line"]}

tree = parser.parse("var x = 1\nvar y = 2")
print(TestTransformer().transform(tree))
