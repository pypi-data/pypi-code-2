from __future__ import division
from pytools import memoize_method
from pymbolic.mapper import RecursiveMapper, CSECachingMapperMixin





class NonlinearityDetector(RecursiveMapper, CSECachingMapperMixin):
    def __init__(self, in_vars):
        RecursiveMapper.__init__(self)
        CSECachingMapperMixin.__init__(self)

        self.in_vars = set(in_vars)

        self.dep_mapper = self.make_dep_mapper()

    @staticmethod
    def make_dep_mapper():
        from pymbolic.mappers import DependencyMapper
        return DependencyMapper(composite_leaves=False)

    @memoize_method
    def contains_vars(self, expr):
        return bool(self.in_vars & self.dep_mapper(expr))

    def map_constant(self, expr):
        return False

    def map_variable(self, expr):
        return False

    def map_call(self, expr):
        # this bluntly assumes the function is nonlinear
        from pytools import any
        return any(self.contains_vars(i) for i in expr.parameters)

    def map_subscript(self, expr):
        return False

    def map_lookup(self, expr):
        return False

    def map_sum(self, expr):
        from pytools import any
        return any(self.rec(ch) for ch in expr.children)

    def map_product(self, expr):
        from pytools import any
        children_nonlin = any(self.rec(ch) for ch in expr.children)
        if children_nonlin:
            return True

        containing_children = [
                ch for ch in expr.children
                if self.contains_vars(ch)]

        return len(containing_children) > 1

    def map_quotient(self, expr):
        return (self.rec(expr.numerator)
                or self.rec(expr.denominator)
                or self.contains_vars(expr.denominator))

    def map_power(self, expr):
        return (self.rec(expr.base)
                or self.rec(expr.exponent)
                or self.contains_vars(expr.base)
                or self.contains_vars(expr.exponent)
                )
        return self.rec(expr.base) or self.rec(expr.exponent)

    def map_polynomial(self, expr):
        # evaluate using Horner's scheme
        result = 0
        if self.rec(expr.base):
            return True

        if self.contains_vars(expr.base):
            for exp, coeff in expr.data:
                if exp not in [0,1]:
                    return True
                if self.contains_vars(coeff):
                    return True
        else:
            return any(self.rec(coeff) for exp, coeff in expr.data)

    def map_list(self, expr):
        from pytools import any
        return any(self.rec(i) for i in expr)

    def map_numpy_array(self, expr):
        from pytools import any, indices_in_shape
        return any(
                self.rec(expr[i])
                for i in indices_in_shape(expr.shape))

    def map_if_positive(self, expr):
        return True

    def map_common_subexpression_uncached(self, expr):
        return self.rec(expr.child)

