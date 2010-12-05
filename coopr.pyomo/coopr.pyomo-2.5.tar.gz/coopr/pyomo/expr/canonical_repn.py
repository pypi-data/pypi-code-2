#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

__all__ = ['generate_canonical_repn', 'as_expr', 'is_constant', 'is_linear', 'is_quadratic', 'is_nonlinear']

import logging

#import pyutilib.component.core
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction, Model, \
                             Constraint, Objective
from coopr.pyomo.base import expr
from coopr.pyomo.base.var import _VarValue, Var
import copy


Logger = logging.getLogger('Pyomo')
#
# A frozen dictionary that can be hashed.  This dictionary isn't _really_
# frozen, but it acts hashable.
#
class frozendict(dict):
    __slots__ = ('_hash',)
    def __hash__(self):
        rval = getattr(self, '_hash', None)
        if rval is None:
            rval = self._hash = hash(frozenset(self.iteritems()))
        return rval

#
# Generate a canonical representation of an expression.
#
# The canonical representation is a dictionary.  Each element is a mapping
# from a term degree to terms in the expression.  If the term degree is
# None, then the map value is simply an expression of terms without a
# specific degree.  Otherwise, the map value is a dictionary of terms to
# their coefficients.  A term is represented as a frozen dictionary that
# maps variable id to variable power.  A constant term is represented
# with None.
#
# Examples:
#  Let x[1] ... x[4] be the first 4 variables, and
#      y[1] ... y[4] be the next 4 variables
#
# 1.3                           {0:{ None :1.3}}
# 3.2*x[1]                      {1:{ {0:1} :3.2}}
# 2*x[1]*y[2] + 3*x[2] + 4      {0:{None:4.0}, 1:{{1:1}:3.0}, 2:{{0:1, 5:1}:2.0}}
# 2*x[1]**4*y[2]    + 4         {0:{None:4.0}, 1:{{1:1}:3.0}, 5:{{0:4, 5:1 }:2.0}}
# log(y[1]) + x[1]*x[1]         {2:{{0:2}:1.0}, None:log(y[1])}
#
def generate_canonical_repn(expr, **kwargs):
    context = kwargs.get('context', None)
    key     = kwargs.get('key', None)

    # Prettify output of user notification "What's it doin' now?!"
    if ( context is not None ):
        name = " '%s" % context.name
        if ( isinstance( context, Constraint ) ):
            item = 'Constraint'
        elif ( isinstance( context, Objective ) ):
            item = 'Objective'
    else:
        item = 'unknown object'
        name = ''
        Logger.info("Argument 'context' not passed")

    if ( key is not None ):
        index = str(key)
        if ( type(key) is tuple ):
            index = index[1:-1] # remove tuple
        index = "[%s]'" % index
    else:
        index = "'"
        if ( '' == name ):
            index = ''

    Logger.info("Generating expression for %(item)s%(name)s%(index)s" %
        { 'item' : item, 'name' : name, 'index' : index } )

    return collect_canonical_repn(expr)


def as_expr(rep, vars=None, model=None, ignore_other=False):
    """ Convert a canonical representation into an expression. """
    if isinstance(model, Model):
        vars = model._var
        id_offset=0
    elif not vars is None:
        id_offset=1
    expr = 0.0
    for d in rep:
        if d is None:
            if not ignore_other:
                expr += rep[d]
            continue
        if d is -1:
            continue
        for v in rep[d]:
            if v is None:
                expr += rep[d][v]
                continue
            e = rep[d][v]
            for id in v:
                for i in xrange(v[id]):
                    if vars is None:
                        e *= rep[-1][id]
                    else:
                        e *= vars[id[1]+id_offset]
            expr += e
    return expr
    
def repn_add(lhs, rhs, coef=1.0):
    """
    lhs and rhs are the expressions being added together.
    'lhs' and 'rhs' are left-hand and right-hand side operands
    See generate_canonical_repn for explanation of pyomo expressions
    """
    for order in rhs:
        # For each order term, first-order might be 3*x,
        # second order 4*x*y or 5*x**2
        if order is None:
            # i.e., (currently) order is a constant or logarithm
            if order in lhs:
                lhs[order] += rhs[order]
            else:
                lhs[order] = rhs[order]
            continue
        if order < 0:
            # ignore now, handled below
            continue
        if not order in lhs:
            lhs[order] = {}
        for var in rhs[order]:
            # Add coefficients of variables in this order (e.g., third power)
            lhs[order][var] = coef*rhs[order][var] + lhs[order].get(var,0.0)
    #
    # Merge the VarValue maps
    #
    if -1 in rhs:
        if -1 in lhs:
            lhs[-1].update(rhs[-1])
        else:
            lhs[-1] = rhs[-1]
    return lhs


def repn_mult(r1, r2, coef=1.0):
    rep = {}
    for d1 in r1:
        for d2 in r2:
            if d1 == None or d2 == None or d1 < 0 or d2 < 0:
                pass
            else:
                d=d1+d2
                if not d in rep:
                    rep[d] = {}
                if d == 0:
                        rep[d][None] = coef * r1[0][None] * r2[0][None]
                elif d1 == 0:
                        for v2 in r2[d2]:
                            rep[d][v2]  = coef * r1[0][None] * r2[d2][v2] + rep[d].get(v2,0.0)
                elif d2 == 0:
                        for v1 in r1[d1]:
                            rep[d][v1]  = coef * r1[d1][v1] * r2[0][None] + rep[d].get(v1,0.0)
                else:
                        for v1 in r1[d1]:
                            for v2 in r2[d2]:
                                v = frozendict(v1)
                                for id in v2:
                                    if id in v:
                                        v[id] += v2[id]
                                    else:
                                        v[id]  = v2[id]
                                rep[d][v] = coef * r1[d1][v1] * r2[d2][v2] + rep[d].get(v,0.0)
    #
    # Handle other nonlinear terms
    #
    if None in r1:
        rep[None] = as_expr(r2, ignore_other=True) * copy.deepcopy(r1[None])
        if None in r2:
            rep[None] += copy.deepcopy(r1[None])*copy.deepcopy(r2[None])
    if None in r2:
        if None in rep:
            rep[None] += as_expr(r1, ignore_other=True) * copy.deepcopy(r2[None])
        else:
            rep[None]  = as_expr(r1, ignore_other=True) * copy.deepcopy(r2[None])
    #
    # Merge the VarValue maps
    #
    if -1 in r1:
        rep[-1] = r1[-1]
    if -1 in r2:
        if -1 in rep:
            rep[-1].update(r2[-1])
        else:
            rep[-1] = r2[-1]
    #
    # Return the canonical repn
    #
    return rep


#
# Temporary canonical expressions
#
# temp_const = { 0: {None:0.0} }    
# temp_var = { 1: {frozendict({None:1}):1.0} }    
# temp_nonl = { None: None }

#
# Internal function for collecting canonical representation, which is
# called recursively.
#
def collect_canonical_repn(exp):
#     global temp_const
#     global temp_var
#     global temp_nonl
    temp_const = { 0: {None:0.0} }    
    temp_var = { 1: {frozendict({None:1}):1.0} }    
    temp_nonl = { None: None }    
    #
    # Ignore identity expressions
    #
    while isinstance(exp, expr._IdentityExpression):
        exp = exp._args[0]
    #
    # Expression
    #
    if isinstance(exp,expr.Expression):
        #
        # Sum
        #
        if isinstance(exp,expr._SumExpression):
            if exp._const != 0.0:
                repn = { 0: {None:exp._const} }    
            else:
                repn = {}
            for i in range(len(exp._args)):
                repn = repn_add(repn, collect_canonical_repn(exp._args[i]), coef=exp._coef[i] )
            return repn
        #
        # Product
        #
        elif isinstance(exp,expr._ProductExpression):
            #
            # Iterate through the denominator.  If they aren't all constants, then
            # simply return this expresion.
            #
            denom=1.0
            for e in exp._denominator:
                if e.fixed_value():
                    #print 'Z',type(e),e.fixed
                    denom *= e.value
                elif e.is_constant():
                    denom *= e()
                else:
                    temp_nonl[None] = exp
                    return temp_nonl
                if denom == 0.0:
                    print "Divide-by-zero error - offending sub-expression:"
                    e.pprint()
                    raise ZeroDivisionError                        
            #
            # OK, the denominator is a constant.
            #
            repn = { 0: {None:exp.coef / denom} }    
            #print "Y",exp.coef/denom
            for e in exp._numerator:
                repn = repn_mult(repn, collect_canonical_repn(e))
            return repn
        #
        # ERROR
        #
        else:
            raise ValueError, "Unsupported expression type: "+str(exp)
    #
    # Constant
    #
    elif exp.fixed_value():
        temp_const[0][None] = exp.value
        return temp_const
    #
    # Variable
    #
    elif type(exp) is _VarValue or exp.type() is Var:
        if type(exp) is _VarValue:
            mid = id(exp.var.model)
        else:
            mid = id(exp.model)
        temp_var = { -1: {(mid,exp.id):exp}, 1: {frozendict({(mid,exp.id):1}):1.0} }    
        return temp_var
    #
    # ERROR
    #
    else:
       raise ValueError, "Unexpected expression type: "+str(exp)



def is_constant(repn):
    """Return True if the canonical representation is a constant expression"""
    for key in repn:
        if key is None or key > 0:
            return False
    return True

def is_nonlinear(repn):
    """Return True if the canonical representation is a nonlinear expression"""
    for key in repn:
        if not key in [-1,0,1]:
            return True
    return False

def is_linear(repn):
    """Return True if the canonical representation is a linear expression."""
    return (1 in repn) and not is_nonlinear(repn)

def is_quadratic(repn):
    """Return True if the canonical representation is a quadratic expression."""
    if not 2 in repn:
        return False
    for key in repn:
        if key is None or key > 2:
            return False
    return True

