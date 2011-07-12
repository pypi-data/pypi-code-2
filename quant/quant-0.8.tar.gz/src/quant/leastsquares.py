import scipy
import numpy
from scipy import linalg
from scipy import matrix
from scipy import array
from scipy import ones
from numpy import ndarray

class LeastSquares(object):

    def __init__(self, xs, y):
        self.pathCount = len(y)
        for x in xs:
            if len(x) != self.pathCount:
                raise Exception, "Regression won't work with uneven path counts."
        self.xs = xs
        self.y = y

    def fit(self):
        regressions = list()
        # Regress against unity.
        regressions.append(ones(self.pathCount))
        # Regress against each variable.
        for x in self.xs:
            regressions.append(x)
        # Regress against squares and cross products.
        indices = range(0, len(self.xs))
        combinations = list()
        for i in indices:
            for j in indices:
                combination = [i, j]
                combination.sort()
                if combination not in combinations:
                    combinations.append(combination)
        for combination in combinations:
            product = self.xs[combination[0]] * self.xs[combination[1]]
            regressions.append(product)
        # Run the regression.
        a = matrix(regressions).transpose()
        b = matrix(self.y).transpose()
        if a.shape[0] != b.shape[0]:
            raise Exception, "Regression won't work with uneven path counts."
        c = self.solve(a, b)
        c = matrix(c)
        #print "a: ", a
        #print "a: ", a.shape, type(a)
        #print "b: ", b
        #print "b: ", b.shape, type(b)
        #print "c: ", c.shape, type(c)
        #print "c: ", c
        if a.shape[1] != c.shape[0]:
            raise Exception, "Matrices are not aligned: %s and %s" % (a.shape, c.shape)
        #else:
        #    raise Exception, "Matrices are aligned: %s and %s" % (a.shape, c.shape)
        d = a * c
        #print "d: ", d
        #print "d: ", d.shape, type(d)
        #print "d A1: ", d.getA1()
        return d.getA1()

    def solve(self, a, b):
        try:
            c,resid,rank,sigma = linalg.lstsq(a, b)
        except Exception, inst:
            msg = "Couldn't solve a and b: ", (a, b)
            raise Exception, msg
        return c

