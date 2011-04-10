"""

Parse simple expressions like "1 + 2 * 4".


From the paper, we call 'nud' prefix, and 'led' infix.  We also call rbp
  right_binding_power, and lbp left_binding_power.
    nud - prefix
    led - infix
    rbp - right_binding_power
    lbp - left_binding_power


We start a JsContext which is an object which will evaluate the expression.
    >>> c = JsContext()

We do a couple of simple tests.
    >>> c.evaluate("1 + 2")
    3.0

    >>> c.evaluate("1 * 2")
    2.0

Now let us trace through a slightly more complex example.
    >>> c.do_logging = True

    >>> c.evaluate("1 + 2 * 4")
    ('token', Literal({'to': 1, 'type': 'number', 'value': 1.0, 'from': 0}))
    ('expression right_binding_power: ', 0)
    ('token', OperatorAdd({'to': 3, 'type': 'operator', 'value': '+', 'from': 2}))
    ('left from prefix of first token', 1.0)
    ('token', Literal({'to': 5, 'type': 'number', 'value': 2.0, 'from': 4}))
    ('expression right_binding_power: ', 10)
    ('token', OperatorMul({'to': 7, 'type': 'operator', 'value': '*', 'from': 6}))
    ('left from prefix of first token', 2.0)
    ('token', Literal({'to': 9, 'type': 'number', 'value': 4.0, 'from': 8}))
    ('expression right_binding_power: ', 20)
    ('token', End({}))
    ('left from prefix of first token', 4.0)
    ('leaving expression with left:', 4.0)
    ('left from previous_token.infix(left)', 8.0)
    right_binding_power:10: token.left_binding_power:0:
    ('leaving expression with left:', 8.0)
    ('left from previous_token.infix(left)', 9.0)
    right_binding_power:0: token.left_binding_power:0:
    ('leaving expression with left:', 9.0)
    9.0
"""


import sys

# let us reuse some code from part1.
sys.path.append("..")
import part1


# a mapping of symbols to Token classes.
symbols = {}

class Token(object):
    def __init__(self, token, context = None):
        self.context = context
        self.token = token

    def __repr__(self):
        #print (dir(self))
        return "%s(%s)" % (self.__class__.__name__, repr(self.token))
        #return self.__classname__


class End(Token):
    left_binding_power = 0
symbols['(end)'] = End

class Literal(Token):
    left_binding_power = 0
    def prefix(self):
        return self.token['value']
symbols['(literal)'] = Literal

class OperatorAdd(Token):
    left_binding_power = 10
    def prefix(self):
        return self.context.expression(100)
    def infix(self, left):
        return left + self.context.expression(self.left_binding_power)
symbols['+'] = OperatorAdd

class OperatorMul(Token):
    left_binding_power = 20
    def prefix(self):
        return self.context.expression(100)
    def infix(self, left):
        return left * self.context.expression(self.left_binding_power)
symbols['*'] = OperatorMul




# We make a new tokenise function which returns a Token subclass for 
# each token in the source code given it.

def tokenise(context, source):
    """ tokenise(context, source) returns a Token
          context - a JsContext to be used for the tokenising.
          source - source code we want to tokenise.
    """
    for t in part1.tokenise(source):
        if t['type'] == "operator":
            yield context.symbols[t['value']](t, context)
        else:
            yield context.symbols['(literal)'](t, context)
    yield context.symbols["(end)"]({}, context)


class JsContext(object):

    def __init__(self, the_symbols = symbols):
        self.symbols = dict(the_symbols)
        self.do_logging = False

    def log(self, val1, val2 = ""):
        if self.do_logging:
            if val2 is not "":
                print (val1, val2)
            else:
                print (val1)

    def expression(self, right_binding_power = 0):
        self.log("expression right_binding_power: ", right_binding_power)

        # we store the previous token and grab a new one.
        previous_token = self.token
        self.token = self.tokens.next()
        self.log("token", self.token)

        # we get the left side of the first token.
        left = previous_token.prefix()
        self.log("left from prefix of first token", left)
        while right_binding_power < self.token.left_binding_power:
            
            previous_token = self.token
            self.token = self.tokens.next()
            self.log("token", self.token)
            left = previous_token.infix(left)
            self.log("left from previous_token.infix(left)", left)
            self.log("right_binding_power:%s: token.left_binding_power:%s:" % (right_binding_power, self.token.left_binding_power))
        self.log("leaving expression with left:", left)
        return left

    def evaluate(self, source):
        """ evaluate(source) returns the result of the expression from the
               give source code.
        """
        self.tokens = tokenise(self, source)
        self.token = self.tokens.next()
        self.log("token", self.token)
        return self.expression()







if __name__ == "__main__":
    import doctest
    doctest.testmod()



