#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Expression', '_LessThanExpression', '_GreaterThanExpression',
        '_LessThanOrEqualExpression', '_GreaterThanOrEqualExpression',
        '_EqualToExpression', '_IdentityExpression' , 'generate_expression']

from plugin import *
from pyutilib.component.core import *
from numvalue import *
from param import _ParamBase
from var import _VarBase

import sys
import copy


class Expression(NumericValue):
    """An object that defines a mathematical expression that can be evaluated"""

    def __init__(self, nargs=-1, name="UNKNOWN", operation=None, args=None, tuple_op=False):
        """Construct an expression with an operation and a set of arguments"""
        NumericValue.__init__(self, name=name)
        self._args=args
        self._nargs=nargs
        self._operation=operation
        self._tuple_op=tuple_op
        self.verify()

    def pprint(self, ostream=None, nested=True, eol_flag=True):
        """Print this expression"""
        if ostream is None:
           ostream = sys.stdout
        if nested:
           print >>ostream, self.name + "(",
           first=True
           for arg in self._args:
             if first==False:
                print >>ostream, ",",
             if isinstance(arg,Expression):
                arg.pprint(ostream=ostream, nested=nested, eol_flag=False)
             else:
                print >>ostream, str(arg),
             first=False
           if eol_flag==True:
              print >>ostream, ")"
           else:
              print >>ostream, ")",

    def clone(self, args=()):
        """Clone this object using the specified arguments"""
        if self.__class__ == Expression:
           return Expression(nargs=self._nargs, name=self.name, operation=self._operation, tuple_op=self._tuple_op, args=args)
        return self.__class__(args=args)

    def verify(self):
        """Throw an exception if the list of arguments differs from the
           specified number of arguments allowed"""
        if self._args is None:
           return
        if (self._nargs != -1) and (self._nargs != len(self._args)):    #pragma:nocover
           raise ValueError, "There were " + `len(self._args)` + " arguments specified for expression " + self.name + " but this expression requires " + `self._nargs` + " arguments"
        for arg in self._args:
            if type(arg) is float:      #pragma:nocover
                raise ValueError, "Argument for expression "+self.name+" is a float!"
            if (isinstance(arg,_ParamBase) or isinstance(arg,_VarBase)) and arg.dim() > 0:
                msg = "Argument for expression '%s' is an n-ary numeric value: %s" % (self.name, arg.name)
                msg += "\n    Have you given variable or parameter '%s' an index?" % arg.name
                raise ValueError, msg

    #
    # this method contrast with the fixed_value() method.
    # the fixed_value() method returns true iff the value is
    # an atomic constant. 
    # this method returns true iff all composite arguments
    # in this sum expression are constant, i.e., numeric 
    # constants or parametrs. the parameter values can of 
    # course change over time, but at any point in time, 
    # they are constant. hence, the name.
    #
    def is_constant(self):
        for arg in self._args:
            if not arg.is_constant():
                return False
        return True

    def simplify(self, model):
        """ Walk through the S-expression, performing simplifications, and
            replacing values of parameters with constants.
        """
        for i in range(0,len(self._args)):
          if isinstance(self._args[i],Expression):
             self._args[i] = self._args[i].simplify(model)
        return self

    def __call__(self, exception=True):
        """Evaluate the expression"""
        values=[]
        for arg in self._args:
          try:
            val = value(arg)
          except ValueError, e:
            if exception:
                raise ValueError, "Error evaluating expression: %s" % str(e)
            return None
          #try:
          #  val = value(arg)
          #except AttributeError:
          #  return None
          if val is None:
             return None
          values.append( val )
        return self._apply_operation(values)

    def _apply_operation(self, values):
        """Method that can be overwritten to re-define the operation in this expression"""
        if self._tuple_op:
           tmp=tuple(values)
           return self._operation(*tmp)
        else:
           return self._operation(values)
        
    def __str__(self):
        return self.name


class _LessThanExpression(Expression):
    """An object that defines a less-than expression"""

    def __init__(self, args=()):
        """Constructor"""
        Expression.__init__(self,args=args,nargs=2,name='lt')

    def _apply_operation(self, values):
        """Method that defines the less-than operation"""
        return values[0] < values[1]


class _GreaterThanExpression(Expression):
    """An object that defines a greater-than expression"""

    def __init__(self, args=()):
        """Constructor"""
        Expression.__init__(self,args=args,nargs=2,name='gt')

    def _apply_operation(self, values):
        """Method that defines the greater-than operation"""
        return values[0] > values[1]


class _LessThanOrEqualExpression(Expression):
    """An object that defines a less-than-or-equal expression"""

    def __init__(self, args=()):
        """Constructor"""
        Expression.__init__(self,args=args,nargs=2,name='lt')

    def _apply_operation(self, values):
        """Method that defines the less-than-or-equal operation"""
        return values[0] <= values[1]


class _GreaterThanOrEqualExpression(Expression):
    """An object that defines a greater-than-or-equal expression"""

    def __init__(self, args=()):
        """Constructor"""
        Expression.__init__(self,args=args,nargs=2,name='gt')

    def _apply_operation(self, values):
        """Method that defines the greater-than-or-equal operation"""
        return values[0] >= values[1]


class _EqualToExpression(Expression):
    """An object that defines a equal-to expression"""

    def __init__(self, args=()):
        """Constructor"""
        Expression.__init__(self,args=args,nargs=2,name='eq')

    def _apply_operation(self, values):
        """Method that defines the equal-to operation"""
        return values[0] == values[1]


class _ProductExpression(Expression):
    """An object that defines a product expression"""

    def __init__(self, args=()):
        """Constructor"""
        self._denominator = []
        self._numerator = list(args)
        self.coef = 1
        Expression.__init__(self,nargs=-1,name='prod')

    def is_constant(self):
        for arg in self._numerator:
            if not arg.is_constant():
                return False
        for arg in self._denominator:
            if not arg.is_constant():
                return False
        return True

    def invert(self):
        tmp = self._denominator
        self._denominator = self._numerator
        self._numerator = tmp
        self.coef = 1.0/self.coef

    def simplify(self, model):
        #
        # First, we apply the standard simplification of arguments
        #
        for i in range(0,len(self._numerator)):
            if isinstance(self._numerator[i],Expression):
                self._numerator[i] = self._numerator[i].simplify(model)
        for i in range(0,len(self._denominator)):
            if isinstance(self._denominator[i],Expression):
                self._denominator[i] = self._denominator[i].simplify(model)
        #
        # Next, we collapse nested products
        #
        tmpnum = []
        tmpdenom = []
        tmpcoef = self.coef
        for arg in self._numerator:
            if isinstance(arg,_ProductExpression):
                tmpnum = tmpnum + arg._numerator
                tmpdenom = tmpdenom + arg._denominator
                tmpcoef *= arg.coef
            else:
                tmpnum.append( arg )
        for arg in self._denominator:
            if isinstance(arg,_ProductExpression):
                tmpnum = tmpnum + arg._denominator
                tmpdenom = tmpdenom + arg._numerator
                if arg.coef != 1:
                    tmpcoef /= 1.0*arg.coef
            else:
                tmpdenom.append( arg )
        if tmpcoef == 0:
           return ZeroConstant
        #
        # Next, we eliminate constants
        #
        newnum = []
        newdenom = []
        newcoef = tmpcoef
        for arg in tmpnum:
            if type(arg) is NumericConstant:
                if arg.value != 1:
                    newcoef *= arg.value
            else:
                newnum.append( arg )
        for arg in tmpdenom:
            if type(arg) is NumericConstant:
                if arg.value != 1:
                    newcoef /= 1.0*arg.value
            else:
                newdenom.append( arg )
        if newcoef == 0:
            return ZeroConstant
        #
        # Return simplified expression
        #
        nargs = len(newnum)+len(newdenom)
        if nargs == 1 and len(newnum) == 1:
            if newcoef == 1:
                return newnum[0]
            if type(newnum[0]) is _SumExpression:
                newnum[0].scale(newcoef)
                return newnum[0]
        if nargs == 0 and newcoef == 1:
           return OneConstant
        self._numerator = newnum
        self._denominator = newdenom
        self.coef = newcoef
        return self

    def add(self,numerator=None,denominator=None):
       # print "TYPE",type(numerator),type(denominator)
        if not numerator is None:
            self._numerator.append(numerator)
            self._nargs += 1
        if not denominator is None:
            self._denominator.append(denominator)
            self._nargs += 1

    def pprint(self, ostream=None, nested=True, eol_flag=True):
        """Print this expression"""
        if ostream is None:
           ostream = sys.stdout
        if nested:
           print >>ostream, self.name + "( num=(",
           first=True
           if self.coef != 1:
                print >>ostream, str(self.coef),
                first=False
           for arg in self._numerator:
             if first==False:
                print >>ostream, ",",
             if isinstance(arg,Expression):
                arg.pprint(ostream=ostream, nested=nested, eol_flag=False)
             else:
                print >>ostream, str(arg),
             first=False
           if first is True:
              print >>ostream, 1,
           print >>ostream, ")",
           if len(self._denominator) > 0:
              print >>ostream, ", denom=(",
              first=True
              for arg in self._denominator:
                if first==False:
                   print >>ostream, ",",
                if isinstance(arg,Expression):
                   arg.pprint(ostream=ostream, nested=nested, eol_flag=False)
                else:
                   print >>ostream, str(arg),
                first=False
              print >>ostream, ")",
           print >>ostream, ")",
           if eol_flag==True:
              print >>ostream, ""

    def clone(self, args=()):
        """Clone this object using the specified arguments"""
        tmp = self.__class__()
        tmp.name = self.name
        tmp.coef = self.coef
        tmp._numerator = copy.copy(self._numerator)
        tmp._denominator = copy.copy(self._denominator)
        return tmp

    def verify(self):
        if self._denominator is None or self._numerator is None:
           return
        for arg in self._numerator:
            if type(arg) is float:      #pragma:nocover
                raise ValueError, "Argument for expression "+self.name+" is a float!"
            if (isinstance(arg,_ParamBase) or isinstance(arg,_VarBase)) and arg.dim() > 0:
                raise ValueError, "Argument for expression "+self.name+" is an n-ary numeric value: "+arg.name
        for arg in self._denominator:
            if type(arg) is float:      #pragma:nocover
                raise ValueError, "Argument for expression "+self.name+" is a float!"
            if (isinstance(arg,_ParamBase) or isinstance(arg,_VarBase)) and arg.dim() > 0:
                raise ValueError, "Argument for expression "+self.name+" is an n-ary numeric value: "+arg.name

    def __call__(self, exception=True):
        """Evaluate the expression"""
        ans = self.coef
        for arg in self._numerator:
            try:
                val = value(arg)
            except ValueError, e:
                if exception:
                    raise ValueError, "Error evaluating expression: %s" % str(e)
                return None
            if val is None:
                return None
            ans *= val
        for arg in self._denominator:
            try:
                val = value(arg)
            except ValueError, e:
                if exception:
                    raise ValueError, "Error evaluating expression: %s" % str(e)
                return None
            if val is None:
                return None
            if val != 1:
                ans /= 1.0*val
        return ans


class _IdentityExpression(Expression):
    """An object that defines a identity expression"""

    def __init__(self, args=()):
        """Constructor"""
        if isinstance(args,list):
           Expression.__init__(self,args=args,nargs=1,name='identity')
        else:
           Expression.__init__(self,args=[args],nargs=1,name='identity')

    def _apply_operation(self, values):
        """Method that defines the identity operation"""
        return values[0]


#class X_NegateExpression(Expression):
    #"""An object that defines a negation expression"""
#
    #def __init__(self, args=()):
        #"""Constructor"""
        #Expression.__init__(self,args=args,nargs=1,name='negate')
#
    #def _apply_operation(self, values):
        #"""Method that defines the negation operation"""
        #return -values[0]


class _AbsExpression(Expression):

    def __init__(self, args=()):
        Expression.__init__(self, args=args, nargs=1, name='abs', operation=abs, tuple_op=True)


class _PowExpression(Expression):

    def __init__(self, args=()):
        Expression.__init__(self, args=args, nargs=2, name='pow', operation=pow, tuple_op=True)


class _SumExpression(Expression):
    """An object that defines a weighted summation of expressions"""

    def __init__(self, args=(), coef=()):
        """Constructor"""
        Expression.__init__(self,args=list(args),nargs=-1,name='sum')
        self._coef = list(coef)
        self._const = 0

    def clone(self, args=()):
        """Clone this object using the specified arguments"""
        tmp = self.__class__()
        tmp.name = self.name
        tmp._args = copy.copy(self._args)
        tmp._nargs = copy.copy(self._nargs)
        tmp._coef = copy.copy(self._coef)
        tmp._const = self._const
        return tmp

    def scale(self, val):
        for i in range(len(self._coef)):
            self._coef[i] *= val
        self._const *= val

    def negate(self):
        self.scale(-1)

    def simplify(self, model):
        #
        # First, we apply the standard simplification of arguments
        #
        Expression.simplify(self,model)
        #
        # Next, we collapse nested sums
        #
        tmpargs = []
        tmpcoef = []
        tmpconst = self._const
        for i in range(len(self._args)):
          arg = self._args[i]
          if isinstance(arg,_SumExpression):
             tmpargs = tmpargs + arg._args
             tmpcoef = tmpcoef + map(lambda x:x*self._coef[i], arg._coef)
             tmpconst += arg._const*self._coef[i]
          else:
             tmpargs.append( arg )
             tmpcoef.append( self._coef[i] )
        #
        # Next, we simplify arguments
        #
        newargs = []
        newcoef = []
        newconst = tmpconst
        for i in range(len(tmpargs)):
            arg = tmpargs[i]
            if type(arg) is NumericConstant:
                if arg.value != 0:
                    newconst += arg.value*tmpcoef[i]
            elif isinstance(arg,_ProductExpression):
                newcoef.append( arg.coef*tmpcoef[i] )
                arg.coef = 1
                newargs.append( arg )
            else:
                newargs.append( arg )
                newcoef.append( tmpcoef[i] )
        #
        # Return simplified expression
        #
        if len(newargs) == 1 and newcoef[0] == 1 and newconst == 0:
           return newargs[0]
        elif len(newargs) > 0 or newconst != 0:
            self._args = newargs
            self._coef = newcoef
            self._const = newconst
            return self
        else:
           return ZeroConstant

    def pprint(self, ostream=None, nested=True, eol_flag=True):
        """Print this expression"""
        if ostream is None:
           ostream = sys.stdout
        if nested:
           print >>ostream, self.name + "(",
           first=True
           if self._const != 0:
                print >>ostream, str(self._const),
                first=False
           for i in range(len(self._args)):
             arg = self._args[i]
             if first==False:
                print >>ostream, ",",
             if self._coef[i] != 1:
                print >>ostream, str(self._coef[i])+" * ",
             if isinstance(arg,Expression):
                arg.pprint(ostream=ostream, nested=nested, eol_flag=False)
             else:
                print >>ostream, str(arg),
             first=False
           print >>ostream, ")",
           if eol_flag==True:
              print >>ostream, ""

    def __call__(self, exception=True):
        """Evaluate the expression"""
        values=[]
        for i in range(len(self._args)):
            arg = self._args[i]
            try:
                val = value(arg)
            except ValueError, e:
                if exception:
                    raise ValueError, "Error evaluating expression: %s" % str(e)
                return None
            if val is None:
                return None
            values.append( self._coef[i]*val )
        return sum(values)+self._const

    def add(self,coef=1,expr=None):
        self._args.append(expr)
        self._coef.append(coef)
        self._nargs += 1


def generate_expression(*_args):
    #print "HERE",_args
    etype = _args[0]

    if etype is 'neg':
        if type(_args[1]) is _SumExpression:
            _args[1].negate()
            return _args[1]
        else:
            etype = 'mul'
            args=[_args[1],-1]
    else:
        args=_args[1:]

    if etype is 'add':
        #
        # self + other
        #
        other = as_numeric(args[1])
        if type(args[0]) is _SumExpression:
            tmp = args[0].clone()
            tmp.add(expr=other)
            return tmp
        else:
            tmp = _SumExpression()
            tmp.add(expr=args[0])
            tmp.add(expr=other)
            return tmp

    elif etype is 'radd':
        #
        # other + self
        #
        other = as_numeric(args[1])
        if type(args[0]) is _SumExpression:
            tmp = args[0].clone()
            tmp.add(expr=other)
            return tmp 
        else:
            tmp = _SumExpression()
            tmp.add(expr=other)
            tmp.add(expr=args[0])
            return tmp

    elif etype is 'sub':
        #
        # self - other
        #
        other = as_numeric(args[1])
        if type(args[0]) is _SumExpression:
            tmp = args[0].clone()
            tmp.add(coef=-1, expr=other)
            return tmp
        else:
            tmp = _SumExpression()
            tmp.add(expr=args[0])
            tmp.add(coef=-1, expr=other)
            return tmp

    elif etype is 'rsub':
        #
        # other - self
        #
        other = as_numeric(args[1])
        if type(args[0]) is _SumExpression:
            tmp = args[0].clone()
            tmp.negate()
            tmp.add(expr=other)
            return tmp
        else:
            tmp = _SumExpression()
            tmp.add(expr=other)
            tmp.add(coef=-1, expr=args[0])
            return tmp

    elif etype is 'mul':
        #
        # self * other
        #
        other = as_numeric(args[1])
        if type(args[0]) is _ProductExpression:
            tmp = args[0].clone()
            tmp.add(numerator=other)
            return tmp
        else:
            tmp = _ProductExpression()
            tmp.add(numerator=args[0])
            tmp.add(numerator=other)
            return tmp

    elif etype is 'rmul':
        #
        # other * self
        #
        other = as_numeric(args[1])
        if type(args[0]) is _ProductExpression:
            tmp = args[0].clone()
            tmp.add(numerator=other)
            return tmp
        else:
            tmp = _ProductExpression()
            tmp.add(numerator=other)
            tmp.add(numerator=args[0])
            return tmp

    elif etype is 'div':
        #
        # self / other
        #
        other = as_numeric(args[1])
        if type(args[0]) is _ProductExpression:
            tmp = args[0].clone()
            tmp.add(denominator=other)
            return tmp
        else:
            tmp = _ProductExpression()
            tmp.add(numerator=args[0])
            tmp.add(denominator=other)
            #print "X",tmp.pprint()
            return tmp

    elif etype is 'rdiv':
        #
        # other / self
        #
        other = as_numeric(args[1])
        if type(args[0]) is _ProductExpression:
            tmp = args[0].clone()
            tmp.invert()
            tmp.add(numerator=other)
            return tmp
        else:
            tmp = _ProductExpression()
            tmp.add(numerator=other)
            tmp.add(denominator=args[0])
            return tmp

    elif etype is 'pow':
        #
        # self ** other
        #
        return _PowExpression([args[0], as_numeric(args[1])])

    elif etype is 'rpow':
        #
        # other ** self
        #
        return _PowExpression([as_numeric(args[1]), args[0]])

    elif etype is 'abs':
        return _AbsExpression([args[0]])


ExpressionRegistration('<', _LessThanExpression)
ExpressionRegistration('lt', _LessThanExpression)
ExpressionRegistration('>', _GreaterThanExpression)
ExpressionRegistration('gt', _GreaterThanExpression)
ExpressionRegistration('<=', _LessThanOrEqualExpression)
ExpressionRegistration('lte', _LessThanOrEqualExpression)
ExpressionRegistration('>=', _GreaterThanOrEqualExpression)
ExpressionRegistration('gte', _GreaterThanOrEqualExpression)
ExpressionRegistration('=', _EqualToExpression)
ExpressionRegistration('eq', _EqualToExpression)

if False:
    ExpressionRegistration('+', _SumExpression)
    ExpressionRegistration('sum', _SumExpression)
    ExpressionRegistration('*', _ProductExpression)
    ExpressionRegistration('prod', _ProductExpression)
    #ExpressionRegistration('-', _MinusExpression)
    #ExpressionRegistration('minus', _MinusExpression)
    #ExpressionRegistration('/', _DivisionExpression)
    #ExpressionRegistration('divide', _DivisionExpression)
    #ExpressionRegistration('-', _NegateExpression)
    #ExpressionRegistration('negate', _NegateExpression)
    ExpressionRegistration('abs', _AbsExpression)
    ExpressionRegistration('pow', _PowExpression)

