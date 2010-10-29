#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

#
# TODO:  Do we need to have different Expression objects for different
#        intrinsic expressions?
# TODO:  If an expression has a fixed value, should we simply call the
#        intrinsic function with the value of that expression?
# TODO:  Do we need to register these expression objects?
#

__all__ = ['log', 'log10', 'sin', 'cos', 'tan', 'cosh', 'sinh', 'tanh', 'asin', 'acos', 'atan', 'exp', 'sqrt', 'asinh', 'acosh', 'atanh']

import component
import expr
import numvalue
import math


class _IntrinsicFuncExpression(expr.Expression):
    """
    An expression class that is used for all intrinsic expressions.
    """

    def __init__(self, args=(), name=None, operation=None):
        expr.Expression.__init__(self, args=args, nargs=len(args), name=name, operation=operation, tuple_op=True)
        self.coef = 1.0

def expr_args(*args):
    """
    Return False if one of the arguments is not an expression or numeric
    value.
    """
    for arg in args:
        if not (isinstance(arg,expr.Expression) or isinstance(arg,numvalue.NumericValue) or isinstance(arg,component.Component)):
            return False
    return True
        


def log(*args):
    if len(args) != 1:
       raise "TypeError: log() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='log', operation=math.log)
    return math.log(*args)

def log10(*args):
    if len(args) != 1:
       raise "TypeError: log10() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='log10', operation=math.log10)
    return math.log10(*args)

def sin(*args):
    if len(args) != 1:
       raise "TypeError: sin() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='sin', operation=math.sin)
    return math.sin(*args)

def cos(*args):
    if len(args) != 1:
       raise "TypeError: cos() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='cos', operation=math.cos)
    return math.cos(*args)

def tan(*args):
    if len(args) != 1:
       raise "TypeError: tan() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='tan', operation=math.tan)
    return math.tan(*args)

def sinh(*args):
    if len(args) != 1:
       raise "TypeError: sinh() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='sinh', operation=math.sinh)
    return math.sinh(*args)

def cosh(*args):
    if len(args) != 1:
       raise "TypeError: cosh() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='cosh', operation=math.cosh)
    return math.cosh(*args)

def tanh(*args):
    if len(args) != 1:
       raise "TypeError: tanh() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='tanh', operation=math.tanh)
    return math.tanh(*args)

def asin(*args):
    if len(args) != 1:
       raise "TypeError: asin() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='asin', operation=math.asin)
    return math.asin(*args)

def acos(*args):
    if len(args) != 1:
       raise "TypeError: acos() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='acos', operation=math.acos)
    return math.acos(*args)

def atan(*args):
    if len(args) != 1:
       raise "TypeError: atan() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='atan', operation=math.atan)
    return math.atan(*args)

def exp(*args):
    if len(args) != 1:
       raise "TypeError: exp() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='exp', operation=math.exp)
    return math.exp(*args)

def sqrt(*args):
    if len(args) != 1:
       raise "TypeError: sqrt() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='sqrt', operation=math.sqrt)
    return math.sqrt(*args)

def asinh(*args):
    if len(args) != 1:
       raise "TypeError: atan() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='asinh', operation=math.asinh)
    return math.asinh(*args)

def acosh(*args):
    if len(args) != 1:
       raise "TypeError: atan() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='acosh', operation=math.acosh)
    return math.acosh(*args)

def atanh(*args):
    if len(args) != 1:
       raise "TypeError: atan() takes exactly 1 argument (%d given)" % len(args)
    if expr_args(*args):
        tmp = list()
        tmp.append(args[0])
        return _IntrinsicFuncExpression(args=tmp, name='atanh', operation=math.atanh)
    return math.atanh(*args)
