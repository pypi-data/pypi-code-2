class IntMonomial(object):
    def __init__(self, c, x):
        self.c = c
        self.x = x

class IntVar(object):
    def __mul__(self, other):
        if isinstance(other, int):
            return IntMonomial(other, self)
        if isinstance(
