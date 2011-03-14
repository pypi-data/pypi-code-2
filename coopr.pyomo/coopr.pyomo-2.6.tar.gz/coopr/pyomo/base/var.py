#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Var', 'VarStatus', '_VarBase', "Piecewise"]

import logging
from component import Component
from numvalue import *
from numvalue import create_name
from label import *
from pyutilib.component.core import alias
import types
from set_types import *
from indexed_component import IndexedComponent
import pyutilib.math
import pyutilib.misc
from pyutilib.enum import Enum
import sys
from param import _ParamValue
from coopr.pyomo.base.util import isfunctor

logger = logging.getLogger('coopr.pyomo')

VarStatus = Enum( 'undefined', 'fixed_by_presolve', 'fixed_by_optimizer',
                  'unused', 'used', )

class _VarValue(NumericValue):
    """Holds the numeric value of a variable"""

    __slots__ = ['var','index','id','label','initial','active','lb','ub','fixed','status','_is_binary','_is_integer','_is_continuous','ampl_var_id']

    def __init__(self, **kwds):
        """Constructor"""

        # NOTE: the "within" keyword takes precedence over the "domain" keyword.
        NumericValue.__init__(self, \
                              name=kwds.get('name', None), \
                              domain=kwds.get('within', kwds.get('domain', Reals)))

        # NOTE: the "name" attribute (part of the base NumericValue class) is 
        #       typically something like some_var[x,y,z] - an easy-to-read
        #       representation of the variable/index pair.

        # NOTE: both of the following are presently set by the parent. arguably, we
        #       should provide keywords to streamline initialization.
        self.var = None # the "parent" variable.
        self.index = None # the index of this variable within the "parent"

        # TBD: Document where this gets populated.
        self.id = None

        # the label is a modification of the input name, with certain symbols
        # that are typically problematic for solver input files re-mapped (e.g., 
        # curly braces) to more friendly symbols. create a default label right
        # away - it can be modified if a particular solver needs it.
        # self.label = None (is set one way or another via the following method)
        self.sync_label()

        # the default initial value for this variable.
        self.initial = None

        # is this variable an active component of the current model?
        self.active = True

        # IMPORTANT: in contrast to the initial value, the lower and upper
        #             bounds of a variable can in principle be either numeric constants,
        #             parameter values, or expressions - anything is OK, as long as
        #             invoking () is legal.
        self.lb = None
        self.ub = None

        self.fixed = False
        self.status = VarStatus.undefined

        # cached for efficiency purposes - isinstance is not cheap.
        self._is_binary = isinstance(self.domain, BooleanSet)
        self._is_integer = isinstance(self.domain, IntegerSet)
        self._is_continuous = not (self._is_binary or self._is_integer)

        # for NL - really a suffix that should be moved to the Var parent class.
        self.ampl_var_id = None

    def __str__(self):
        # the name can be None, in which case simply return "".
        if self.name is None:
           return ""
        else:
           return self.name

    def __getstate__(self):
       result = NumericValue.__getstate__(self)
       for i in _VarValue.__slots__:
          result[i] = getattr(self, i)
       return result

    def sync_label(self):
        if self.name is not None:
           self.label = label_from_name(self.name)
           if (self.var is not None) and (self.var.model is not None):
              self.var.model._name_varmap[self.label] = self
        else:
           self.label = None

    def getattrvalue(self, attr_name):
       if attr_name not in self.var._attr_values:
          raise RuntimeError,"Variable="+str(self.var.name)+" does not have an attributed defined with name="+str(attr_name)
       return self.var._attr_values[attr_name][self.index]

    def setattrvalue(self, attr_name, attr_value):
       if attr_name not in self.var._attr_values:
          raise RuntimeError,"Variable="+str(self.var.name)+" does not have an attributed defined with name="+str(attr_name)        
       self.var._attr_values[attr_name][self.index] = attr_value

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False

    def setlb(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore
        # complex numbers).
        if value is None:
            self.lb = None
        elif isinstance(value, (int, long, float)):
            self.lb = NumericConstant(value=value)
        elif isinstance(value, _ParamValue):
            self.lb = value
        else:
            msg = "Unknown type '%s' supplied as variable lower bound - "     \
                  'legal types are numeric constants or parameters'
            raise ValueError, msg % str( type(value) )

    def setub(self, value):
        # python only has 3 numeric built-in type that we deal with (we ignore
        # complex numbers).
        if isinstance(value, (int, long, float)):
            self.ub = NumericConstant(value=value)
        elif value is None:
            self.ub = None
        elif isinstance(value, _ParamValue):
            self.ub = value
        else:
            msg = "Unknown type '%s' supplied as variable lower bound - "     \
                  'legal types are numeric constants or parameters'
            raise ValueError, msg % str( type(value) )


    def fixed_value(self):
        if self.fixed:
            return True
        return False

    def is_constant(self):
        if self.fixed:
            return True
        return False

    def polynomial_degree(self):
        if self.fixed:
            return 0
        return 1

    def is_binary(self):
        return self._is_binary

    def is_integer(self):
        return self._is_integer

    def is_continuous(self):
        return self._is_continuous

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, str(self),

    def _tighten_bounds(self):
        """
        Attempts to tighten the lower- and upper-bounds on this variable
        by using the domain.
        """
        try:
            dbounds = self.domain.bounds()
        except:
            # No explicit domain bounds
            return

        if self.lb is None or \
               (dbounds[0] is not None and dbounds[0] > self.lb.value):
            self.setlb(dbounds[0])

        if self.ub is None or \
               (dbounds[1] is not None and dbounds[1] < self.ub.value):
            self.setub(dbounds[1])


#
# Variable attributes:
#
# Single variable:
#
# x = Var()
# x.fixed = True
# x.domain = Reals
# x.name = "x"
# x.setlb(-1.0)
# x.setub(1.0)
# x.initial = 0.0
# x = -0.4
#
# Array of variables:
#
# y = Var(set1,set2,...,setn)
# y.fixed = True (fixes all variables)
# y.domain = Reals
# y.name = "y"
# y[i,j,...,k] (returns value of a given index)
#
# y[i,j,...,k].fixed
# y[i,j,...,k].lb()
# y[i,j,...,k].ub()
# y[i,j,...,k].initial
#

class _VarBase(IndexedComponent):
    """A numeric variable, which may be defined over a index"""

    """ Constructor
        Arguments:
           name         The name of this variable
           index        The index set that defines the distinct variables.
                          By default, this is None, indicating that there
                          is a single variable.
           domain       A set that defines the type of values that
                          each parameter must be.
           default      A set that defines default values for this
                          variable.
           bounds       A rule for defining bounds values for this
                          variable.
           rule         A rule for setting up this parameter with
                          existing model data
    """
    # TODO: default and rule keywords are not used?  Need to talk to Bill ...?
    def __init__(self, *args, **kwd):
        tkwd = {'ctype':Var}
        IndexedComponent.__init__(self, *args, **tkwd)

        # Default keyword values
        #
        self._attr_declarations = {} # maps the name of an attribute (i.e., a suffix) to its default value.
        self._attr_values = {} # maps the name of an attribute to a dictionary containing (index, value) pairs.
        self._varval = {}
        self._initialize = kwd.pop('initialize', None )
        self.name   = kwd.pop('name', 'unknown')
        self.domain = kwd.pop('within', Reals )
        self.domain = kwd.pop('domain', self.domain )
        self.bounds = kwd.pop('bounds', None )
        self.doc    = kwd.pop('doc', None )

        self._binary_keys = []
        self._continuous_keys = []
        self._integer_keys = []

        # Check for domain rules
        if isfunctor(self.domain):
            self._domain_rule = self.domain

            # Individual variables will be restricted
            self.domain = None
        else:
            self._domain_rule = None

        if kwd:
            msg = "Var constructor: unknown keyword '%s'"
            raise ValueError, msg % kwd.keys()[0]

    def as_numeric(self):
        if None in self._varval:
            return self._varval[None]
        return self

    def is_indexed(self):
        return self._ndim > 0

    def is_expression(self):
        return False

    def is_relational(self):
        return False

    def keys(self):
        return self._varval.keys()

    def binary_keys(self):
        """ Returns the keys of all binary variables """
        return self._binary_keys

    def continuous_keys(self):
        """ Returns the keys of all continuous variables """
        return self._continuous_keys

    def integer_keys(self):
        """ Returns the keys of all integer variables """
        return self._integer_keys

    def __iter__(self):
        return self._varval.keys().__iter__()

    def __contains__(self,ndx):
        return ndx in self._varval

    def dim(self):
        return self._ndim

    def reset(self):
        for value in self._varval.itervalues():
            value.set_value(value.initial)

    def __len__(self):
        return len(self._varval)

    def __setitem__(self,ndx,val):
        #print "HERE",ndx,val, self._valid_value(val,False), self.domain
        if (None in self._index) and (ndx is not None):
            # allow for None indexing if this is truly a singleton
            msg = "Cannot set an array value in singleton variable '%s'"
            raise KeyError, msg % self.name

        if ndx not in self._index:
            msg = "Cannot set the value of array variable '%s' with invalid " \
                  "index '%s'"
            raise KeyError, msg % ( self.name, str(ndx) )

        if not self._valid_value(val,False):
            msg = "Cannot set variable '%s[%s]' with invalid value: %s"
            raise ValueError, msg % ( self.name, str(ndx), str(val) )
        self._varval[ndx].value = val

    def __getitem__(self,ndx):
        """This method returns a _VarValue object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        try:
            return self._varval[ndx]
        except KeyError: # thrown if the supplied index is hashable, but not defined.
            msg = "Unknown index '%s' in variable %s;" % (str(ndx), self.name)
            if (isinstance(ndx, (tuple, list)) and len(ndx) != self.dim()):
                msg += "    Expecting %i-dimensional indices" % self.dim()
            else:
                msg += "    Make sure the correct index sets were used.\n"
                msg += "    Is the ordering of the indices correct?"
            raise KeyError, msg
        except TypeError, msg: # thrown if the supplied index is not hashable
            msg2 = "Unable to index variable %s using supplied index with " % self.name
            msg2 += str(msg)
            raise TypeError, msg2

    def _add_domain_key(self, ndx, domain):
        """ Register an index with a specific set of keys """
        if isinstance(domain, BooleanSet):
            self._binary_keys.append(ndx)
        elif isinstance(domain, IntegerSet):
            self._integer_keys.append(ndx)
        else:
            self._continuous_keys.append(ndx)

    def construct(self, data=None):
        if __debug__:   #pragma:nocover
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Variable, name=%s, from data=%s", self.name, `data`)
        if self._constructed:
            return
        self._constructed=True
        #
        # Construct _VarValue() objects for all index values
        #
        if self._ndim > 0:
            if type(self._initialize) is dict:
                self._index = self._initialize.keys()

            for ndx in self._index:
                # Check for domain rules
                if self._domain_rule is not None:
                    domain = self._domain_rule(ndx, self.model)
                    if isinstance(domain, BooleanSet):
                        self._binary_keys.append(ndx)
                    elif isinstance(domain, IntegerSet):
                        self._integer_keys.append(ndx)
                    else:
                        self._continuous_keys.append(ndx)
                else:
                    domain = self.domain
                    self._add_domain_key(ndx, domain)

                self._varval[ndx] = _VarValue(
                      name = create_name(self.name,ndx),
                      domain = domain,
                      )

                self._varval[ndx].var = self
                self._varval[ndx].index = ndx
        else:
           # if the dimension is a singleton (i.e., we're dealing
           # with a _VarElement), then the name was set after
           # the VarValue construction for the singleton - and as
           # a consequence, the label attribute has yet to be defined.
           # so set it! 
           if self.name is not None:
              self._varval[None].label = label_from_name(self.name)

        #
        # Define the _XXX_keys objects if domain isn't a rule;
        # they were defined individually above in the case of
        # a rule
        #
        if not self._domain_rule is not None:
            if isinstance(self.domain, BooleanSet):
                self._binary_keys = self._varval.keys()
            elif isinstance(self.domain, IntegerSet):
                self._integer_keys = self._varval.keys()
            else:
                self._continuous_keys = self._varval.keys()

        #
        # Initialize values with a dictionary if provided
        #
        if self._initialize is not None:
            #
            # Initialize values with the _rule function if provided
            #
            if self._initialize.__class__ is types.FunctionType:
                for key in self._varval:
                    if key is None:
                        tmp = []
                    elif key.__class__ is tuple:
                        tmp = list(key)
                    else:
                        tmp = [key]
                    tmp.append(self.model)
                    val = self._initialize(*tuple(tmp))
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
            elif self._initialize.__class__ is dict:
                for key in self._initialize:
                    val = self._initialize[key]
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
            else:
                for key in self._index:
                    val = self._initialize
                    self._valid_value(val, True)
                    self._varval[key].value = self._varval[key].initial = val
        #
        # Initialize bounds with the bounds function if provided
        #
        if self.bounds is not None:

           if type(self.bounds) is tuple:

              # bounds are specified via a tuple - same lower and upper bounds for all var values!

              (lb, ub) = self.bounds
              
              # do some simple validation that the bounds are actually finite - otherwise, set them to None.        
              if (lb is not None) and (not pyutilib.math.is_finite(value(lb))):
                 lb = None
              if (ub is not None) and (not pyutilib.math.is_finite(value(ub))):
                 ub = None

              for key,varval in self._varval.iteritems():
                 if lb is not None:
                    varval.setlb(lb)
                 if ub is not None:
                    varval.setub(ub)

           else:

             # bounds are specified via a function

             for key in self._varval:
               if isinstance(key,tuple):
                  tmp = list(key)
               elif key is None:
                  tmp = []
               else:
                  tmp = [key]
               tmp.append(self.model)
               tmp = tuple(tmp)
               (lb, ub) = self.bounds(*tmp)
               self._varval[key].setlb(lb)
               self._varval[key].setub(ub)

               for key in self._varval:
                  if self._varval[key].lb is not None and not pyutilib.math.is_finite(self._varval[key].lb()):
                     self._varval[key].setlb(None)
                  if self._varval[key].ub is not None and not pyutilib.math.is_finite(self._varval[key].ub()):
                     self._varval[key].setub(None)
        #
        # Iterate through all variables, and tighten the bounds based on
        # the domain bounds information.
        #
        # Only done if self.domain is not a rule. If it is, _VarArray level
        # bounds become meaningless, since the individual _VarElement objects
        # likely have more restricted domains.
        #
        if self._domain_rule is None:
            dbounds = self.domain.bounds()
            if not dbounds is None and dbounds != (None,None):
                for key in self._varval:
                    if not dbounds[0] is None:
                        if self._varval[key].lb is None or                     \
                            dbounds[0] > self._varval[key].lb():
                            self._varval[key].setlb(dbounds[0])

                    if not dbounds[1] is None:
                        if self._varval[key].ub is None or                     \
                            dbounds[1] < self._varval[key].ub():
                            self._varval[key].setub(dbounds[1])
        #
        # Setup declared attributes for all variables
        #
        for attr_name in self._attr_declarations:
            default_value = self._attr_declarations[attr_name][0]
            suffix_dict = {}
            for key in self._varval:
                suffix_dict[key]=default_value
            self._attr_values[attr_name] = suffix_dict
        #
        # update the parent model (if any) name->var map.
        #
        if self.model is not None:
           for varval in self._varval.itervalues():
              self.model._name_varmap[varval.label] = varval

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self)),
        if self.domain is not None:
            print >>ostream, "\tDomain="+self.domain.name
        else:
            print >>ostream, "\tDomain=None"
        if self._index_set is not None:
            print >>ostream, "\tIndicies: ",
            for idx in self._index_set:
               print >>ostream, str(idx.name)+", ",
            print ""
        if None in self._varval:
           print >>ostream, "\tInitial Value : Lower Bound : Upper Bound : "  \
                            "Current Value: Fixed: Status"
           lb_value = None
           if self._varval[None].lb is not None:
              lb_value = self._varval[None].lb()
           ub_value = None
           if self._varval[None].ub is not None:
              ub_value = self._varval[None].ub()

           print >>ostream, "\t %s : %s : %s : %s : %s : %s" % (
             str(self._varval[None].initial),
             str(lb_value),
             str(ub_value),
             str(self._varval[None].value),
             str(self._varval[None].fixed),
             str(self._varval[None].status)
           )
        else:
           print >>ostream, "\tKey : Initial Value : Lower Bound : "          \
                            "Upper Bound : Current Value: Fixed: Status"
           tmp=self._varval.keys()
           tmp.sort()
           for key in tmp:
             initial_val = self._varval[key].initial
             lb_value = None
             if self._varval[key].lb is not None:
                lb_value = self._varval[key].lb()
             ub_value = None
             if self._varval[key].ub is not None:
                ub_value = self._varval[key].ub()

             print >>ostream, "\t%s : %s : %s : %s : %s : %s : %s" % (
               str(key),
               str(initial_val),
               str(lb_value),
               str(ub_value),
               str(value(self._varval[key].value)),
               str(value(self._varval[key].fixed)),
               str(self._varval[key].status)
             )


    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Variable "+self.name,":",
        print >>ostream, "  Size="+str(len(self)),
        print >>ostream, "Domain="+self.domain.name
        if None in self._varval:
           print >>ostream, "%s  Value=%s" % (
             prefix,
             pyutilib.misc.format_io(self._varval[None].value)
           )
        else:
           for key in self._varval:
             val = self._varval[key].value
             print >>ostream, prefix+"  "+str(key)+" : "+str(val)

    def declare_attribute(self, name, default=None):
        """
        Declare a user-defined attribute.
        """
        if name[0] == "_":
            msg = "Cannot define an attribute that begins with  '_'"
            raise AttributeError, msg
        if name in self._attr_declarations:
            raise AttributeError, "Attribute %s is already defined" % name
        self._attr_declarations[name] = (default,)
        #if not default is None:
            #self._valid_value(default)
        #
        # If this variable has been constructed, then
        # generate this attribute for all variables
        #
        # add to self._attr_values
        if len(self._varval) > 0:
            suffix_dict = {}
            for key in self._varval:
                suffix_dict[key]=default
            self._attr_values[name] = suffix_dict

    def attribute_defined(self, name):
        """
        Determine if a user-defined attribute actually exists!        
        """
        return name in self._attr_declarations

# a _VarElement is the implementation representing a "singleton" or non-indexed variable.
# NOTE: this class derives from both a "slot"ized base class (_VarValue) and a normal
#       class with a dictionary (_VarBase) - beware (although I believe the __getstate__
#       implementation should be attribute-independent).

class _VarElement(_VarBase, _VarValue):

    def __init__(self, *args, **kwd):

        _VarValue.__init__(self, **kwd)
        _VarBase.__init__(self, *args, **kwd)
        self._varval[None] = self
        self._varval[None].var = self
        self._varval[None].index = None

    def __call__(self, exception=True):
        if None in self._varval:
            return self._varval[None].value
        return None

    def __getstate__(self):
       result = _VarValue.__getstate__(self)
       for key,value in self.__dict__.iteritems():
          result[key]=value
       return result

    def is_constant(self):
       return _VarValue.is_constant(self)

# a _VarArray is the implementation representing an indexed variable.

class _VarArray(_VarBase):

    def __init__(self, *args, **kwd):

        _VarBase.__init__(self, *args, **kwd)
        self._dummy_val = _VarValue(**kwd)

    def __float__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def __int__(self):
        raise TypeError, "Cannot access the value of array variable "+self.name

    def _valid_value(self,value,use_exception=True):
        #print "VALID",self._dummy_val.domain
        return self._dummy_val._valid_value(value,use_exception)

    def set_value(self, value):
        msg = "Cannot specify the value of array variable '%s'"
        raise ValueError, msg % self.name

    def __str__(self):
        return self.name

    def construct(self, data=None):
        _VarBase.construct(self, data)

        for (ndx, var) in self._varval.iteritems():
            var._tighten_bounds()


class Var(Component):
    """
    Variable objects that are used to construct Pyomo models.
    """

    alias("Var", "Decision variables in a model.")

    def __new__(cls, *args, **kwds):
        if args == ():
            self = _VarElement(*args, **kwds)
        else:
            self = _VarArray(*args, **kwds)
        return self


class Piecewise(_VarArray):
    """
    A piecewise linear expression.

    Usage:

    model.X = Var() # pre-requisite

    # Let breakpoint_rule and slope_rule define a piecewise linear
    # function f(x) when indexed over sets (...)
    #
    # Then model.XF is a variable constrained by model.XF = f(model.X)
    model.XF = Piecewise(
                         breakpoint_rule=breakPointRule,
                         slope_rule=slopeRule,
                         offset=0,
                         value=model.X,
                         forcesos2=True
                         )

    # Evaluate the piecewise expression at 7.0
    model.C2.eval(7.0)

    Breakpoints refer to the values on the domain that separate the
    domain into distinct intervals. All intervals are assumed to be
    closed on the lower bound and open on the upper bound, with the
    exception of the interval extending to negative infinity on the
    lower bound. The first slope specified is assumed to be the slope
    of an interval coming from negative infinity to the first
    breakpoint; all other slopes are assumed to correspond to the
    intervals between the current and next breakpoint. The offset
    keyword is used to indicate the y-intercept of the expression
    (default is zero).

    Example:

    The concave function

           / 2x + 3, x < 0
    f(x) = | 3,      0 < x < 1
           \ 3 - x,  1 < x

    would be modeled as:

    breakpoints = [0, 1]
    slopes = [2, 0, -1]
    offset = 3

    If the function should have a bounded domain, specify more
    breakpoints than slopes.

    Example:

    The concave function

           / 2x + 3, -2 < x < 0
    f(x) = | 3,       0 < x < 1
           \ 3 - x,   1 < x < 4

    would be modeled as:

    breakpoints = [-2, 0, 1, 4]
    slopes = [2, 0, -1]
    offset = 3

    If we model a bounded domain, the variable passed to model.value
    will be bounded by this domain. Finally, for bounded domains, the
    offset is the vertical offset of the leftmost breakpoint.

    The forcesos2 keyword is simply used to always generate the sos2
    transformation, even if the slopes specify a concave/convex function.

    """

    alias("Piecewise", "A variable constrained by a piecewise function.")

    def __init__(self, *args, **kwargs):
        """
        Create a new Piecewise variable
        """

        # ---------------------------------------------------------------------
        # Process arguments

        # We can either get explicit breakpoints and slopes, or rules
        # defining them. 
        self._breakpoints = kwargs.pop('breakpoints', None)
        self._slopes = kwargs.pop('slopes', None)

        self._breakpoint_rule = kwargs.pop('breakpoint_rule', None)
        self._slope_rule = kwargs.pop('slope_rule', None)

        self._forcesos2 = kwargs.pop('forcesos2', False)

        # The corresponding domain variable.
        self.variable = kwargs.pop('value', None)

        # The y-intercept of the entire piecewise construct.
        self.offset = kwargs.pop('offset', 0)

        # Don't pop the name, we want to pass this to superclass constructor
        tmpname = kwargs.get('name', 'unknown')

        # ---------------------------------------------------------------------
        # Error checking

        # Make sure a domain variable was passed.
        if self.variable is None:
            raise TypeError, "Specify a Variable object for the 'value' " \
                  "attribute for Piecewise object '%s'" % tmpname

        # Make sure repetitive arguments aren't specified
        if self._breakpoints is not None and self._breakpoint_rule is not None:
            raise TypeError, "Specify only one of 'breakpoints' and " \
                  "'breakpointrule' in Piecewise object '%s'" % tmpname
        if self._slopes is not None and self._slope_rule is not None:
            raise TypeError, "Specify only one of 'slopes' and " \
                  "'sloperule' in Piecewise object '%s'" % tmpname

        # Make sure enough arguments were specified
        if self._breakpoints is None and self._breakpoint_rule is None:
            raise TypeError, "Specify exactly one of 'breakpoints' or " \
                  "'breakpointrule' in Piecewise object '%s'" % tmpname
        if self._slopes is None and self._slope_rule is None:
            raise TypeError, "Specify exactly one of 'slopes' or " \
                  "'sloperule' in Piecewise object '%s'" % tmpname

        # ---------------------------------------------------------------------
        # Initialization

        # NOTE: The following is a bit confusing. _VarElement is in turn derived from _VarBase,
        #       which is in turn derived from IndexedComponent. if the component really isn't
        #       indexed, then self._ndim will equal 0. 
        # 
        _VarArray.__init__(self, *args, **kwargs)

        # If index sets were passed to either breakpoint or slopes,
        # make sure the appropriate rule is defined.
        if (self._ndim > 0) and (self._breakpoint_rule is None):
            raise TypeError, "Cannot specify an indexed Piecewise variable without " \
                  "'breakpoint_rule': object='%s'" % tmpname
        if (self._ndim > 0) and (self._slope_rule is None):
            raise TypeError, "Cannot specify an indexed Piecewise variable without " \
                  "'slope_rule': object='%s'" % tmpname

    def construct(self, data=None):
        """
        Construct the breakpoint and slope expressions
        """

        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Constructing Piecewise component, name=%s, from data=%s", self.name, `data`)

        # take care of the base variable array first.
        _VarArray.construct(self, data)           

        # NOTE: the _breakvals and _slopevals attributes can be either lists (if the 
        #       component is not indexed) or list of lists (if the component is indexed).

        # Construct the breakpoints
        self._breakvals = list()
        if self._breakpoints is not None:
            # Unpack breakpoints from an iterable
            for exp in self._breakpoints:
                if exp is not None:
                    self._breakvals.append(exp)
        else:
            # Get breakpoints from a rule
            if (self._ndim == 0):
                # Rule isn't indexed
                exp = self._breakpoint_rule((self.model,))
                if not isinstance(exp, (list, tuple)):
                   raise TypeError, "A breakpoint rule is expected to return a list or a tuple - returned type was "+str(type(exp))
                if exp is not None:
                    self._breakvals = exp
            else:
                # component is indexed
                for index in self._index:
                    # Make index a list, and then append self.model
                    if isinstance(index, (list, tuple)):
                        index = list(index)
                    else:
                        index = [index]
                    index.append(self.model)

                    # Get the next breakpoint
                    exp = self._breakpoint_rule(*index)
                    if exp is not None:
                        self._breakvals.append(exp)

        # Construct the slopes
        self._slopevals = list()
        if self._slopes is not None:
            # Unpack slopes from an iterable
            for exp in self._slopes:
                if exp is not None:
                    self._slopevals.append(exp)
        else:
            # Get slopes from a rule
            if (self._ndim == 0):
                # Rule isn't indexed
                exp = self._slope_rule((self.model,))
                if not isinstance(exp, (list, tuple)):
                   raise TypeError, "A slope rule is expected to return a list or a tuple - returned type was "+str(type(exp))
                if exp is not None:
                    self._slopevals = exp
            else:
                # component is indexed
                for index in self._index:
                    # Make index a list, and then append self.model
                    if isinstance(index, (list, tuple)):
                        index = list(index)
                    else:
                        index = [index]
                    index.append(self.model)

                    # Get the next breakpoint
                    exp = self._slope_rule(*index)
                    if exp is not None:
                        self._slopevals.append(exp)

        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                if (self._ndim == 0):
                    logger.debug("Slopes="+str(self._slopevals))
                else:
                    i = 0
                    for index in self._index:
                        logger.debug("Slope["+str(index)+"]="+str(self._slopevals[i]))
                        i += 1

                if (self._ndim == 0):
                    logger.debug("Breakpoints="+str(self._breakvals))
                else:
                    i = 0
                    for index in self._index:
                        logger.debug("Breakpoint["+str(index)+"]="+str(self._breakvals[i]))
                        i += 1

        # If N breakpoints are specified, then there can be N-1 or N+1 slopes.
        if (self._ndim == 0):
           if abs(len(self._slopevals) - len(self._breakvals)) != 1:
               msg = "Error constructing Piecewise object '%(name)s'; "          \
                     "%(breaks)i breakpoints and %(slopes)i slopes were "        \
                     "specified.\n\tGiven %(breaks)i breakpoints, there should " \
                     "be %(breaks)i-1 or %(breaks)i+1 slopes."
               raise ValueError, msg % {
                 "breaks" : len(self._breakvals),
                 "slopes" : len(self._slopevals),
                 "name"   : self.name
               }
        else:
           for i in range(0,len(self._breakvals)):
              if abs(len(self._slopevals[i]) - len(self._breakvals[i])) != 1:
                  msg = "Error constructing Piecewise object '%(name)s'; "          \
                        "%(breaks)i breakpoints and %(slopes)i slopes were "        \
                        "specified.\n\tGiven %(breaks)i breakpoints, there should " \
                        "be %(breaks)i-1 or %(breaks)i+1 slopes."
                  raise ValueError, msg % {
                    "breaks" : len(self._breakvals[i]),
                    "slopes" : len(self._slopevals[i]),
                    "name"   : self.name
                  }

        # If a user specified an unbounded problem, add "None" to both ends of self._breakvals.
        if (self._ndim == 0):
           if len(self._breakvals) < len(self._slopevals):
              self._breakvals.insert(0, None)
              self._breakvals.append(None)
        else:
           for i in range(0,len(self._breakvals)):
              if len(self._breakvals[i]) < len(self._slopevals[i]):
                 self._breakvals[i].insert(0, None)
                 self._breakvals[i].append(None)

        # Finally, generate the constraints for each index (if applicable).
        if (self._ndim == 0):
           self._generate_constraints(None, self._breakvals, self._slopevals)
        else:
           i = 0
           for index in self._index:
              self._generate_constraints(index, self._breakvals[i], self._slopevals[i])
              i += 1


    def _concave_or_convex(self):
        """
        Determines if the expressions forms a concave or convex expression.
        Returns -1 if concave, 1 if convex, 2 if affine, and 0 otherwise.
        """

        # Must be convex if there are less than three segments
        if len(self._slopevals) <= 2:
            if len(self._slopevals) == 1:
                # Affine
                return 2
            elif self._slopevals[0] < self._slopevals[1]:
                # Convex
                return 1
            elif self._slopevals[0] == self._slopevals[1]:
                # Affine
                return 2
            else:
                # Concave
                return -1

        # Find first segment that doesn't have the same slope,
        # get initial direction
        start = 1
        while start < len(self._slopevals):
            if value(self._slopevals[start]) == \
                   value(self._slopevals[start-1]):
                start += 1
            else:
                direction = value(self._slopevals[start]) > \
                            value(self._slopevals[start-1])
                break

        # If we didn't find a change in slope, we're affine
        if start == len(self._slopevals) - 1:
            # Affine
            return 2

        # Make sure the rest of the segments follow the same direction
        for i in xrange(start, len(self._slopevals)):
            if not (direction and value(self._slopevals[i]) >= \
                    value(self._slopevals[i-1])):
                return 0

        if direction:
            # Convex
            return 1
        else:
            # Concave
            return -1

    def is_convex(self):
        res = self._concave_or_convex()
        return res == 1 or res == 2

    def is_concave(self):
        res = self._concave_or_convex()
        return res == -1 or res == 2

    def is_affine(self):
        return self._concave_or_convex() == 2

    def is_concave_or_convex(self):
        return self._concave_or_convex() != 0

    def _generate_constraints(self, index, breakvals, slopevals):
        """
        Generate the constraints on the variable. If this is a convex
        (or concave) expression, then we simply minimize (or maximize)
        over a number of linear constraints. If not, we introduce SOS2
        variables to constrain the expression.
        """

        # Error if imported at module level
        from constraint import Constraint, SOSConstraint
        from rangeset import RangeSet

        # The root of all implicit constraint, variable, and set names
        baseName = str(self.name) + "[" + str(index) + "]" + "_implicit_"

        # Make a partial closure that returns a rule
        # Arguments passed become closures
        def makeRule(index, slope, hOffset, vOffset):
            expr = slope*(self.variable[index] - hOffset) + vOffset
            if convex:
                def rule(model):
                    return self[index] >= expr
            else:
                def rule(model):
                    return self[index] <= expr
            return rule

        def makeBoundRule(index, value, greater=True):
            if greater:
                def rule(model):
                    return self.variable[index] >= value
            else:
                def rule(model):
                    return self.variable[index] <= value
            return rule

        # Bound model.value if domain is bounded
        if (breakvals[0] is not None):
            self.model.__setattr__(
                baseName + "value_lower_bound",
                Constraint(rule=makeBoundRule(index, breakvals[0], True))
                )
        if (breakvals[-1] is not None):
            self.model.__setattr__(
                baseName + "value_upper_bound",
                Constraint(rule=makeBoundRule(index, breakvals[-1], False))
                )

        convex = self.is_convex()
        concave = self.is_concave()
        if (convex or concave) and (self._forcesos2 is False):
            
            # Maximize (convex) or minimize (concave) over all
            # constraints We first find the interval containing zero

            # Handle the case where the domain has no lower bound.
            if breakvals[0] is None:
                start = 1

                # Line segment with a lower domain bound of -inf
                self.model.__setattr__(
                    baseName + "constraint[%i]" % 0,
                    Constraint(rule=makeRule(index,
                                             slopevals[0],
                                             breakvals[1],
                                             self.offset
                                             ))
                    )
            else:
                start = 0

            # Create the rest of the constraints. Walk from the lower
            # to upper bounds of the domain, keeping track of the
            # vertical offset.
            offset = self.offset
            i = start
            stop = len(breakvals)-1
            if (breakvals[-1] is None):
                stop -= 1

            while i <= stop:
                slope = slopevals[i]
                # Make constraint
                self.model.__setattr__(
                    baseName + "constraint[%i]" % i,
                    Constraint(rule=makeRule(index,
                                             slope,
                                             breakvals[i],
                                             offset))
                    )

                # Update offset
                if i < stop:
                    offset += slope*(breakvals[i+1] - breakvals[i])

                i += 1

        else:
            # Introduce SOS2 constraints

            # IMPORTANT
            #
            # For now, we assume that the domain is bounded. It will
            # fail otherwise. Support for extended domains coming
            # soon.

            # Hack to artificially bound the problem, if necessary
            if breakvals[0] is None:
                breakvals = breakvals[1:]
                slopevals = slopevals[1:]
            if breakvals[-1] is None:
                breakvals = breakvals[:-1]
                slopevals = slopevals[:-1]

            # Walk the breakpoints of the function and find the associated
            # images
            images = [self.offset]
            i = 0
            stop = len(slopevals) - 1
            while i <= stop:
                images.append(
                    images[-1] + slopevals[i] * \
                    (breakvals[i+1] - breakvals[i])
                    )
                i += 1

            # Make the new set indexing the variables
            setName = baseName + "SOS_index_set"
            self.model.__setattr__(
                setName,
                RangeSet(0, len(breakvals)-1)
                )

            # Make the new variables
            varName = baseName + "SOS_variables"
            self.model.__setattr__(
                varName,
                Var(self.model.__getattribute__(setName))
                )

            # Constrain variables

            # It would be nice to just bound all the SOS variables in the
            # Var() class, but then if the variable doesn't appear anywhere
            # else in the LP file CPLEX fails, so we explicity constrain
            # them here

            def makeBoundsRule(varName):
                def boundsRule(i, model):
                    return (0, model.__getattribute__(varName)[i], 1)
                return boundsRule

            self.model.__setattr__(
                baseName + "bounds_constraint",
                Constraint(self.model.__getattribute__(setName),
                           rule=makeBoundsRule(varName))
                )

            # The SOS2 variables sum to 1
            def makeSumRule(varName, setName):
                def sumRule(model):
                    sum(model.__getattribute__(varName)[i] for i in \
                        model.__getattribute__(setName)) == 1
                return sumRule

            self.model.__setattr__(
                baseName + "sum_constraint",
                Constraint(rule=makeSumRule(varName, setName)))

            # The variable self is a convex combination of the images

            def makeImageConvexCombRule(varName, setName, images):
                def imageConvexCombRule(model):
                    return self == sum(
                        model.__getattribute__(varName)[i] * images[i] \
                        for i in model.__getattribute__(setName))

                return imageConvexCombRule

            self.model.__setattr__(
                baseName + "image_convex_combination_constraint",
                Constraint(rule=makeImageConvexCombRule(varName,
                                                        setName,
                                                        images))
                )

            # The variable model.value is a convex combination of the
            # breakpoints

            def makeDomainConvexCombRule(index, varName, setName, breakpoints):
                def domainConvexCombRule(model):
                    return self.variable[index] == sum(
                        model.__getattribute__(varName)[i] * breakpoints[i] \
                        for i in model.__getattribute__(setName))

                return domainConvexCombRule

            self.model.__setattr__(
                baseName + "domain_convex_combination_constraint",
                Constraint(rule=makeDomainConvexCombRule(index,
                                                         varName,
                                                         setName,
                                                         breakvals
                                                         )))

            # Finally, nonzero auxialliary variables must be adjacent
            self.model.__setattr__(
                baseName + "SOS2_constraint",
                SOSConstraint(var=self.model.__getattribute__(varName),
                              set=self.model.__getattribute__(setName),
                              sos=2))

