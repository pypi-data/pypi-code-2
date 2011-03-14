#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['value', 'NumericValue', 'as_numeric', 'NumericConstant', 'ZeroConstant', 'OneConstant', 'is_constant']

import plugin
import pyutilib.math
import sys
from set_types import Reals, Any


##------------------------------------------------------------------------
##
## Standard types of expressions
##
##------------------------------------------------------------------------

def create_name(name, ndx):
    if ndx is None:
        return name
    if type(ndx) is tuple:
        tmp = str(ndx).replace(', ',',')
        return name+"["+tmp[1:-1]+"]"
    return name+"["+str(ndx)+"]"

def value(obj):
    """
    A utility function that returns the value of a Pyomo object or expression.

    If the argument is None, a numeric value or a string, then this function simply
    returns the argument.  Otherwise, if the argument is a NumericValue then the
    __call__ method is executed.
    """
    if obj is None:
        return None
    if type(obj) in (bool,int,long,float,str):
        return obj
    if not isinstance(obj, NumericValue):
        raise ValueError, "Object "+str(obj)+" is not a NumericValue object"
    tmp = obj()
    if tmp is None:
        raise ValueError, "No value for uninitialized NumericValue object "+obj.name
    return tmp

def is_constant(obj):
    """
    A utility function that returns a boolean that indicates whether the object is a constant
    """
    if obj.__class__ is int or obj.__class__ is float:
        return True
    try:
        return obj.is_constant()
    except AttributeError:
        if obj.__class__ is (obj + 0).__class__ or \
                obj.__class__ is bool:
            return True
    except:
        pass
    raise ValueError, "This object is not a numeric value: "+str(obj)

def as_numeric(obj):
    """Verify that this obj is a NumericValue or intrinsic value"""
    if obj.__class__ is int or obj.__class__ is float:
        return NumericConstant(value=obj)
    try:
        return obj.as_numeric()
    except AttributeError:
        pass
    try:
        if obj.__class__ is (obj + 0).__class__ or \
                obj.__class__ is bool:
            return NumericConstant(value=obj)
    except:
        pass
    raise ValueError, "This object is not a numeric value: "+str(obj)


class NumericValue(object):
    """An object that contains a numeric value"""

    __slots__ = ['name','domain','value']

    __hash__ = None

    #
    # kwargs are a nice programmer convenience, but their manipulation appears too expensive in a highly used base class.
    #
    # the validate_value argument only applies to the value supplied in the constructor, and does not prevent 
    # subsequent value assignments from being checked.
    #
    def __init__(self, name=None, value=None, domain=None, validate_value=True):
        self.name = name
        self.domain = domain

        if (value and pyutilib.math.is_nan(value)):
            value = pyutilib.math.nan

        # a numeric value is only constrained by the domain,
        # if specified. avoid invoking set_value() here to
        # accelerate object construction, which takes
        # significant time due to the typical number of
        # occurrences. similarly, we are avoiding the
        # invocation of _valid_value. 
        if (value is not None) and (validate_value is True) and (self.domain is not None) and (value not in self.domain):
           raise ValueError, "Numeric value `"+str(value)+"` is not in domain "+str(self.domain)            

        self.value = value

    # defining slots requires the definition of __getstate__ and __setstate__ for pickle'ing.
    # each derived class needs to over-ride this method to both call the base class method
    # (which will populate the dictionary with slots specific to the base class, and to add
    # any slots to the dictionary unique to the derived class.
    def __getstate__(self):
       return dict((i, getattr(self, i)) for i in NumericValue.__slots__)
    
    def __setstate__(self, data_dict):
       for (slot_name, value) in data_dict.iteritems():
          setattr(self, slot_name, value)
        
    def is_constant(self):
        return True

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def is_indexed(self):
        return False

    def polynomial_degree(self):
        return 0

    def fixed_value(self):
        return False

    def as_numeric(self):
        return self

    def pprint(self, ostream=None):
        raise IOError, "NumericValue:pprint is not defined"     #pragma:nocover

    def display(self, ostream=None):
        self.pprint(ostream=ostream)

    def reset(self):            #pragma:nocover
        pass                    #pragma:nocover

    def set_value(self, val):
        if self._valid_value(val):
            self.value=val

    def __nonzero__(self):
        if self.value is None:
            raise ValueError, "Numeric value is undefined"
        if self.value:
            return True
        return False

    def __call__(self, exception=True):
        return self.value

    def __float__(self):
        tmp = self.__call__()
        if tmp is None:
            raise ValueError, "Cannot coerce numeric value `"+self.name+"' to float because it is uninitialized."
        return float(tmp)

    def __int__(self):
        tmp = self.__call__()
        if tmp is None:
            raise ValueError, "Cannot coerce numeric value `"+self.name+"' to integer because it is uninitialized."
        return int(tmp)

    def _valid_value(self,value,use_exception=True):
        #print "HERE X", self.domain is None
        ans = value is None or self.domain is None or value in self.domain
        if not ans and use_exception:
           raise ValueError, "Numeric value `"+str(value)+"` is not in domain "+str(self.domain)
        return ans

    def X__getattr__(self,name):
        #print "GETATTR",name
        #d = self.__dict__
        try:
            return self.__dict__[name]
        except:
            pass
        try:
            return self.__dict__["_attr_"+name]
        except:
            pass
        raise AttributeError, "Unknown attribute `"+str(name)+"' for object with type "+str(type(self))

    def X__setattr__(self,name,val):
        ##print "SETATTR",name,val
        if name == "__class__":
           self.__class__ = val
           return
        if name[0] == "_":
           self.__dict__[name] = val
           return
        if name in self._standard_attr:
           self.__dict__["_attr_"+name] = val
           return
        raise AttributeError, "Unallowable attribute `"+name+"`"
        #self._standard_attr[name] = val

    def __lt__(self,other):
        """Less than operator

        (Called in response to 'self < other' or 'other > self'.)
        """
        return expr.generate_relational_expression('<', self, as_numeric(other))

    def __gt__(self,other):
        """Greater than operator

        (Called in response to 'self > other' or 'other < self'.)
        """
        return expr.generate_relational_expression('<', as_numeric(other), self)

    def __le__(self,other):
        """Less than or equal operator

        (Called in response to 'self <= other' or 'other >= self'.)
        """
        return expr.generate_relational_expression('<=', self, as_numeric(other))

    def __ge__(self,other):
        """Greater than or equal operator

        (Called in response to 'self >= other' or 'other <= self'.)
        """
        return expr.generate_relational_expression('<=', as_numeric(other), self)

    def __eq__(self,other):
        """Equal to operator

        (Called in response to 'self = other'.)
        """
        return expr.generate_relational_expression('==', self, as_numeric(other))

    def __add__(self,other):
        """Binary addition

        (Called in response to 'self + other'.)
        """
        return expr.generate_expression('add',self,other)

    def __sub__(self,other):
        """ Binary subtraction

        (Called in response to 'self - other'.)
        """
        return expr.generate_expression('sub',self,other)

    def __mul__(self,other):
        """ Binary multiplication

        (Called in response to 'self * other'.)
        """
        return expr.generate_expression('mul',self,other)

    def __div__(self,other):
        """ Binary division

        (Called in response to 'self / other'.)
        """
        return expr.generate_expression('div',self,other)

    def __pow__(self,other):
        """ Binary power

        (Called in response to 'self ** other'.)
        """
        return expr.generate_expression('pow',self,other)

    def __radd__(self,other):
        """Binary addition

        (Called in response to 'other + self'.)
        """
        return expr.generate_expression('radd',self,other)

    def __rsub__(self,other):
        """ Binary subtraction

        (Called in response to 'other - self'.)
        """
        return expr.generate_expression('rsub',self,other)

    def __rmul__(self,other):
        """ Binary multiplication

        (Called in response to 'other * self'.)
        """
        return expr.generate_expression('rmul',self,other)
        
    def __rdiv__(self,other):
        """ Binary division

        (Called in response to 'other / self'.)
        """
        return expr.generate_expression('rdiv',self,other)

    def __rpow__(self,other):
        """ Binary power

        (Called in response to 'other ** self'.)
        """
        return expr.generate_expression('rpow',self,other)

    def __iadd__(self,other):
        """Binary addition

        (Called in response to 'self += other'.)
        """
        return expr.generate_expression('iadd',self,other)

    def __isub__(self,other):
        """ Binary subtraction

        (Called in response to 'self -= other'.)
        """
        return expr.generate_expression('isub',self,other)

    def __imul__(self,other):
        """ Binary multiplication

        (Called in response to 'self *= other'.)
        """
        return expr.generate_expression('imul',self,other)
        
    def __idiv__(self,other):
        """ Binary division

        (Called in response to 'self /= other'.)
        """
        return expr.generate_expression('idiv',self,other)

    def __ipow__(self,other):
        """ Binary power

        (Called in response to 'self **= other'.)
        """
        return expr.generate_expression('ipow',self,other)

    def __neg__(self):
        """ Negation

        (Called in response to '- self'.)
        """
        return expr.generate_expression('neg',self)

    def __pos__(self):
        """ Positive expression

        (Called in response to '+ self'.)
        """
        return self

    def __abs__(self):
        """ Absolute value

        (Called in response to 'abs(self)'.)
        """
        return expr.generate_expression('abs',self)


class NumericConstant(NumericValue):
    """An object that contains a constant numeric value"""

    __slots__ = [] # adds no attributes above and beyond those defined in the base clss.

    def __init__(self, name=None, domain=None, value=None):
        if domain is None:
           domain = Reals
        # NOTE: we in general don't perform domain validation of numeric constants,
        #       especially because the user/caller has specified the value, and 
        #       typically does not specify the domain. The domain might be useful 
        #       with meta-level symbolic expression analysis, but for now we treat this as
        #       a Any.
        NumericValue.__init__(self, name=name, domain=domain, value=value, validate_value=False)

    def fixed_value(self):
        return True

    def __call__(self, exception=True):
        return self.value

    def __str__(self):
        return str(self.value)

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, str(self),


ZeroConstant = NumericConstant(value=0)
OneConstant = NumericConstant(value=1)

import expr
