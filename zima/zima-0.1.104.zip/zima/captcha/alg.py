# Algebraic captcha

import random

from helpers import mutateToFormulaImg

class Captcha():

    operators = ['+', '-', '*']
    variables = ['a', 'b', 'c', 'd', 'm', 'n']
    coefficients = ['3', '5', '7', '11']

    def __init__(self, cfg):
        
        self._cfg = cfg

    def _print(self, expr, onTop=False):
        if isinstance(expr, str):
            return expr
        elif isinstance(expr, int):
            return str(expr)
        elif expr[0] == '*' and isinstance(expr[1], str) and isinstance(expr[2], str):
            return expr[1]+expr[2]
        elif expr[0] == '/':
            return r'\frac{%s}{%s}' % (self._print(expr[1]), self._print(expr[2]))
        elif expr[0] == '*':
            return self._print(expr[1])+r'\cdot '+self._print(expr[2])
        else:
            if onTop:
                return self._print(expr[1])+expr[0]+self._print(expr[2])
            else:
                return r'\left('+self._print(expr[1])+expr[0]+self._print(expr[2])+r'\right)'

    def _mutate(self, expr, mutations):
        if mutations > self._cfg.mutationsNum:
            return expr
        else:
            if random.randint(0,10) % 3 == 1:
                m = random.randint(2,4)
                d = random.randint(2,4)
                return self._mutate([expr[0],
                         ['/',
                          ['-', 
                           ['*', expr[1], str(m * d)], 
                           ['*', expr[1], str(m * d - d)]],
                          str(d)],
                         self._mutate(expr[2], mutations+1)], mutations + 1)
            if random.randint(0,10) % 3 == 2:
                var = random.choice(self.variables)
                d = str(random.randint(2,4))
                return self._mutate(['+', 
                              ['/', var, d], 
                              ['/', 
                               ['-', 
                                ['*', d, expr], 
                                var], 
                               d]], mutations + 1)
            else:
                return self._mutate(expr, mutations + 1)

    def generate(self):
        vrs = random.sample(self.variables, 3)
        ops = random.sample(self.operators, 2)
        coefs = random.sample(self.coefficients, 3)
        store = [ops[0], 
                ['*', coefs[0], vrs[0]], 
                [ops[1], 
                 ['*', coefs[1], vrs[1]], 
                 ['*', coefs[2], vrs[2]]]]
        return store, mutateToFormulaImg(
            self._print(self._mutate(store, 0), True))

    def check(self, answer):
        pass

def test():
    class Cls():
        pass
    a = Cls()
    a.mutationsNum = 1
    cap = Captcha(a)
    return cap.generate()

if __name__ == '__main__':
    print test()
