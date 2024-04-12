import pyparsing as pp

class ModalLogicParser:
    def __init__(self):
        # Define the grammar
        self.atom = pp.Word(pp.alphas)
        self.formula = pp.Forward()
        self.unary_op = pp.Literal("~") | pp.Literal("[]") | pp.Literal("<>")  # Modal operators
        self.binary_op = pp.Literal("&") | pp.Literal("|") | pp.Literal("->")
        self.expr = pp.Forward()
        self.paren_expr = pp.nestedExpr(opener='(', closer=')', content=self.expr)
        self.formula << (self.atom | self.unary_op + self.formula | self.paren_expr)
        self.expr << pp.infixNotation(self.formula, [
            (pp.oneOf("& |"), 2, pp.opAssoc.LEFT),
            (pp.Literal("->"), 2, pp.opAssoc.RIGHT),
            (pp.oneOf("[] <> ~"), 1, pp.opAssoc.LEFT)
        ]).setParseAction(self.flatten)

    def flatten(self, tokens):
        if len(tokens) == 1:
            return tokens[0]
        return tokens.asList()

    def parse(self, s):
        return self.expr.parseString(s, parseAll=True)
