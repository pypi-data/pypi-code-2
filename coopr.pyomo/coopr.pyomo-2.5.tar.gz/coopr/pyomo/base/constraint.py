#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Constraint', 'SOSConstraint', 'ConstraintBase']

import sys

from expr import *
from indexed_component import IndexedComponent
from numtypes import *
from numvalue import *
from numvalue import create_name
from pyutilib.component.core import alias
from sets import _BaseSet, _SetContainer, _ProductSet
from var import Var, _VarValue, _VarArray, _VarElement
from objective import Objective
import pyomo
import pyutilib.math
import pyutilib.misc

from component import Component
from set_types import *
from sets import _SetContainer

class ConstraintBase(IndexedComponent):
    """
    Abstract base class for all constraint types. Keeps track of how many
    constraint objects are in existence.
    """

    alias("ConstraintBase", "Abstract base class for all model constraints")

    # The number of explicit constraints declared.
    _nExplicitConstraints = 0

    def __init__(self, *args, **kwargs):
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        ctype = {'ctype': kwargs.pop("ctype", None)}
        IndexedComponent.__init__(self, *args, **ctype)

        tmpname  = kwargs.pop('name', 'unknown')
        self.doc = kwargs.pop('doc', None )

        # Increment the class count
        ConstraintBase._inc_count()

        self._data = {}

    def dim(self):
        return self._ndim

    def __len__(self):
        return len(self._data.keys())

    def keys(self):
        return self._data.keys()
        #return self._index

    def __contains__(self,ndx):
        return ndx in self._data
        #return ndx in self._index

    def __getitem__(self, ndx):
        """This method returns a ConstraintData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._data:
            return self._data[ndx]
        msg = "Unknown index in constraint '%s': %s"
        raise KeyError, msg % ( self.name, str(ndx) )

    def __iter__(self):
        return self._data.keys().__iter__()

    def __del__(self):
        """ Remove this constraint from the count """
        self._inc_count(-1)

    @classmethod
    def _inc_count(cls, n=1):
        """ Alter the constraint count """
        cls._nExplicitConstraints += n

    @classmethod
    def num_explicit_constraints(cls):
        return cls._nExplicitConstraints


class ConstraintData(NumericValue):

    def __init__(self, name=None):
        NumericValue.__init__(self,name=name,domain=Reals)
        self._equality = False
        self.lower = None
        self.lower_ineq_strict = None
        self.lin_body = None # a linear compilation of the source expressions tree.
        self.body = None # an expression tree encoding of the constraint body. if None, an alternative representation (e.g., lin_body) will be != None.
        self.upper = None
        self.upper_ineq_strict = None
        self.label = None
        self.id = None
        self.active = True

    def __call__(self, exception=True):
        if self.body is None:
            return None
        return self.body()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Constraint(NumericValue, ConstraintBase):
    """An object that defines a objective expression"""

    alias("Constraint", "Constraint expressions a model.")

    def __init__(self, *args, **kwargs):
        """
        Construct an objective expression with rule to construct the
        expression

        keyword arguments:
        name: name of this object
        rule: function or rule definition of constraint
        expr: same as rule
        doc:  documentation string for constraint
        """
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        # See if 'ctype' was passed as a keyword argument;
        # this allows derived classses to alert Pyomo to
        # their existence through super() calls. If not,
        # pass Constraint
        tkwd = {'ctype': kwargs.pop('ctype', Constraint)}

        # Pass some arguments to ConstraintBase
        tkwd['doc'] = kwargs.pop('doc', None)
        tkwd['name'] = kwargs.get('name', 'unknown')

        ConstraintBase.__init__(self, *args, **tkwd)

        tmpname = kwargs.pop('name', 'unknown')
        tmprule = kwargs.pop('rule', None )
        tmprule = kwargs.pop('expr', tmprule )

        self._no_rule_init = kwargs.pop('noruleinit', None )

        if ( kwargs ): # if dict not empty, there's an error.  Let user know.
            msg = "Creating constraint '%s': unknown option(s)\n\t%s"
            msg = msg % ( tmpname, ', '.join(kwargs.keys()) )
            raise ValueError, msg

        # _no_rule_init is a flag specified by the user to indicate that no
        # construction rule will be specified, and that constraints will be
        # explicitly added by the user. set via the "noruleinit" keyword. value
        # doesn't matter, as long as it isn't "None".

        self._data = {}

        NumericValue.__init__(self,name=tmpname)
        if None in self._data:
            # As far as I can tell, this never executes? 2010 Jun 08
            self._data[None].name=tmpname
        self.rule = tmprule
        self.trivial = False # True if all constraint indicies have trivial expressions.

    def clear(self):
        self._data = {}

    def __call__(self, exception=True):
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].body is None:
                return None
            return self._data[None].body()
        if exception:
            msg = 'Cannot compute the value of an array of constraints'
            raise ValueError, msg


    def construct(self, data=None, simplify=True):

        if pyomo.debug("verbose") or pyomo.debug("normal"):     #pragma:nocover
            print "Constructing constraint "+self.name
        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for constraint '%s'; defaulting to "     \
                  'rule-based construction.'
            print msg % self.name
        if self.rule is None:
            if self._no_rule_init is None:
                msg = 'WARNING: No construction rule or expression '          \
                      "specified for 'constraint '%s'"
                print msg % self.name
            return
        if self._constructed:
            return
        self._constructed=True
        #
        # Local variables for code optimization
        #

        _self_rule = self.rule
        #
        if isinstance(_self_rule,Expression):
            if not None in self._index:
                msg = 'Cannot define multiple indices in a constraint with '  \
                      'a single expression'
                raise IndexError, msg
            self.add(None, _self_rule, simplify)
        else:
            for val in self._index:
                if pyomo.debug("verbose"):                      #pragma:nocover
                    print "   Constructing constraint index "+str(val)
                if val is None:
                    expr = _self_rule(self.model)
                    if expr is None or (type(expr) in (int, long, float) \
                                        and expr == 0):
                        continue
                else:
                    if type(val) is tuple:
                        tmp=list(val)
                    else:
                        tmp=[val]
                    tmp.append(self.model)
                    tmp=tuple(tmp)
                    expr = _self_rule(*tmp)
                    if expr is None or (type(expr) in (int, long, float) \
                                        and expr == 0):
                        continue
                ##constructed_indices.append(val)
                self.add(val, expr, simplify)
        #self._index=constructed_indices

    def add(self, index, expr, simplify=True):

        # index: the constraint index (should probably be renamed)
        # expr: the constraint expression

        #
        # Ignore an 'empty' constraint
        #
        if expr is None:
            return

        # Verify that the user actually provided an expression or tuple/list --
        # they can (and have) specified odd expressions that evaluate to
        # unexpected values, e.g., True or False.
        #
        if not isinstance(expr, (Expression, list, tuple)):
            msg = 'Non-expression object of %s supplied to initialize '       \
                  'constraint %s[%s]'
            raise ValueError, msg % ( str(type(expr)), self.name, str(index) )

        # Local variables to optimize runtime performance
        #
        _self_data = self._data
        _self_data[index] = ConstraintData(name=create_name(self.name,index))
        if not type(expr) in [tuple,list]:
            _expr_args0 = expr._args[0]
            _expr_args1 = expr._args[1]

            #_expr_args0.pprint()
            #print "HERE", is_constant(_expr_args0)
            #_expr_args1.pprint()
            #print "HERE", is_constant(_expr_args1)

        greater = (_GreaterThanExpression, _GreaterThanOrEqualExpression )
        less    = (_LessThanExpression,    _LessThanOrEqualExpression )
        # If the constructor rule returns an equality expression, then
        # convert to a 3-tuple
        #
        if isinstance(expr,_EqualToExpression):
            _self_data[index]._equality = True
            if is_constant(_expr_args1):
                tpl = [ _expr_args1,_expr_args0,_expr_args1, False, False ]
            elif is_constant(_expr_args1):
                tpl = [ _expr_args0,_expr_args1,_expr_args0, False, False ]
            else:
                tpl = [ 0.0 , _expr_args0 - _expr_args1, 0.0, False, False ]
        #
        # If the constructor rule returns a greater-than expression, then
        # convert to a 3-tuple
        #
        elif isinstance(expr, greater):

            if isinstance(_expr_args0, greater ):
                tpl = [ _expr_args1, _expr_args0._args[1], _expr_args0._args[0],
                        isinstance(expr,_GreaterThanExpression),
                        isinstance(_expr_args0,_GreaterThanExpression) ]

            elif isinstance(_expr_args0, less ):
                tpl = [ _expr_args1, _expr_args0._args[0], _expr_args0._args[1],
                        isinstance(expr,_GreaterThanExpression),
                        isinstance(_expr_args0,_LessThanExpression) ]

            elif isinstance(_expr_args1, greater ):
                tpl = [ _expr_args1._args[1], _expr_args1._args[0], _expr_args0,
                        isinstance(_expr_args1, _GreaterThanExpression),
                        isinstance(expr,_GreaterThanExpression) ]

            elif isinstance(_expr_args1, less ):
                tpl = [ _expr_args1._args[0], _expr_args1._args[1], _expr_args0,
                        isinstance(_expr_args1,_LessThanExpression),
                        isinstance(expr,_GreaterThanExpression) ]

            elif isinstance(_expr_args0,_EqualToExpression) or\
                    isinstance(_expr_args1,_EqualToExpression):
                msg = 'Bound error: > expression used with an = expression.'
                raise ValueError, msg

            elif _expr_args0.is_constant():
                tpl = [ None, _expr_args1, _expr_args0,
                        True, isinstance(expr,_GreaterThanExpression) ]
            elif _expr_args1.is_constant():
                tpl = [ _expr_args1, _expr_args0, None,
                        isinstance(expr,_GreaterThanExpression), True]
            else:
                tpl = [ 0.0, _expr_args0-_expr_args1, None,
                        isinstance(expr,_GreaterThanExpression), True ]

        #
        # If the constructor rule returns a less-than expression, then
        # convert to a 3-tuple
        #
        elif isinstance(expr, less ):

            if isinstance(_expr_args0, less ):
                tpl = [ _expr_args0._args[0],_expr_args0._args[1],_expr_args1,
                        isinstance(_expr_args0,_LessThanExpression),
                        isinstance(expr,_LessThanExpression) ]

            elif isinstance(_expr_args0, greater ):
                tpl = [ _expr_args0._args[1],_expr_args0._args[0],_expr_args1,
                        isinstance(_expr_args0,_GreaterThanExpression),
                        isinstance(expr,_LessThanExpression) ]

            elif isinstance(_expr_args1, less ):
                tpl = [ _expr_args0,_expr_args1._args[0],_expr_args1._args[1],
                        isinstance(expr,_LessThanExpression),
                        isinstance(_expr_args1,_LessThanExpression) ]

            elif isinstance(_expr_args1, greater ):
                tpl = [ _expr_args0,_expr_args1._args[1],_expr_args1._args[0],
                        isinstance(expr,_LessThanExpression),
                        isinstance(_expr_args1,_GreaterThanExpression) ]

            elif isinstance(_expr_args0,_EqualToExpression) or\
                    isinstance(_expr_args1,_EqualToExpression):
                msg = 'Bound error: < expression used with = expression.%s%s'
                raise ValueError, msg % ( str(expr), str(expr._args) )

            elif _expr_args0.is_constant():
                tpl = [ _expr_args0, _expr_args1, None,
                        isinstance(expr,_LessThanExpression), True ]
            elif _expr_args1.is_constant():
                tpl = [ None, _expr_args0, _expr_args1,
                        True, isinstance(expr,_LessThanExpression) ]
            else:
                tpl = [ 0.0, _expr_args1 - _expr_args0, None,
                        isinstance(expr,_LessThanExpression), True ]
        #
        # If the constructor rule returns a tuple or list, then convert
        # it into a canonical form
        #
        elif type(expr) in [tuple,list]:
            #
            # Convert tuples to list
            #
            if type(expr) is tuple:
                expr = list(expr)
            #
            # Form equality expression
            #
            if len(expr) == 2:
                _self_data[index]._equality = True
                if is_constant(expr[1]):
                    tpl = [ expr[1], expr[0], expr[1], False, False ]
                else:
                    tpl = [ expr[0], expr[1], expr[0], False, False ]
            #
            # Form inequality expression
            #
            elif len(expr) == 3:
                tpl=list(expr)+[expr[0] is None, expr[2] is None]
            else:
                msg = "Constructor rule for constraint '%s' returned a tuple" \
                      ' of length %d.  Expecting a tuple of length 2 or 3:\n' \
                      'Equality:   (left, right)\n' \
                      'Inequality: (lower, variable, upper)'
                raise ValueError, msg % ( self.name, len(expr) )

        # Unrecognized constraint values
        #
        else:
            msg = "Constraint '%s' does not have a proper value.  Found '%s'\n"\
                  'Expecting a tuple or equation.  Examples:\n\n' \
                  ' return summation( model.costs ) == model.income\n' \
                  ' return (0, model.price[ item ], 50)'
            raise ValueError, msg % ( self.name, str(expr) )
        #
        # Replace numeric bound values with a NumericConstant object,
        # and reset the values to 'None' if they are 'infinite'
        #
        if type(tpl[0]) in (bool, int, long, float):
            if pyutilib.math.is_finite(tpl[0]):
                tpl[0] = NumericConstant(value=float(tpl[0]))
            else:
                tpl[0] = None
        elif type(tpl[0]) is NumericConstant and                              \
                              not pyutilib.math.is_finite(tpl[0]()):
            tpl[0] = None
        if type(tpl[1]) in (bool, int, long, float):
            msg = "Constraint '%s', index='%s', has a numeric body with value=%s; an expression is expected."
            raise ValueError, msg % (self.name , str(index), str(tpl[1]))

        if _self_data[index]._equality:
            tpl[2] = tpl[0]
        elif type(tpl[2]) in (bool, int, long, float):
            if pyutilib.math.is_finite(tpl[2]):
                tpl[2] = NumericConstant(value=float(tpl[2]))
            else:
                tpl[2] = None
        elif type(tpl[2]) is NumericConstant and                              \
                              not pyutilib.math.is_finite(tpl[2]()):
            tpl[2] = None

        # Error check, to ensure that we don't have an equality constraint with
        # 'infinite' RHS
        #
        if (tpl[0] is None or tpl[2] is None) and _self_data[index]._equality:
            msg = "Equality constraint '%s' defined with infinite RHS"
            raise ValueError, msg % self.name

        # Setup identity expressions
        #
        if tpl[0] is not None:
            if not isinstance(tpl[0],Expression):
                tpl[0] = _IdentityExpression(tpl[0])
            if simplify is True:
               tpl[0] = tpl[0].simplify(self.model)
        if tpl[1] is not None:
            if not isinstance(tpl[1],Expression):
                tpl[1] = _IdentityExpression(tpl[1])
            if simplify is True:
               tpl[1] = tpl[1].simplify(self.model)
        if tpl[2] is not None:
            if not isinstance(tpl[2],Expression):
                tpl[2] = _IdentityExpression(tpl[2])
            if simplify is True:
               tpl[2] = tpl[2].simplify(self.model)
        #
        # Finally, setup the data
        #
        _self_data[index].lower = tpl[0]
        _self_data[index].lower_ineq_strict = tpl[3]
        _self_data[index].body = tpl[1]
        _self_data[index].upper = tpl[2]
        _self_data[index].upper_ineq_strict = tpl[4]


    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
           print >>ostream, "\tIndex=",self._index.name
        else:
           print >>ostream,""
        for val in self._data:
          if not val is None:
             print >>ostream, "\t"+`val`
          if self._data[val].lower is not None:
             print >>ostream, "\t\t",
             self._data[val].lower.pprint(ostream)
          else:
             print >>ostream, "\t\t-Inf"
          if self._data[val].lower_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].body is not None:
             print >>ostream, "\t\t",
             self._data[val].body.pprint(ostream)
          #else:                         #pragma:nocover
             #raise ValueError, "Unexpected empty constraint body"
          if self._data[val].upper_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].upper is not None:
             print >>ostream, "\t\t",
             self._data[val].upper.pprint(ostream)
          elif self._data[val]._equality:
             print >>ostream, "\t\t",
             self._data[val].lower.pprint(ostream)
          else:
             print >>ostream, "\t\tInf"

    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Constraint "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
            if self._data[None].body is None:
                val = 'none'
            else:
                val = pyutilib.misc.format_io(self._data[None].body())
            print >>ostream, '%s  Value=%s' % (prefix, val)
        else:
           flag=True
           for key in self._data:
             if not self._data[key].active:
                continue
             if flag:
                print >>ostream, prefix+"        \tLower\tBody\t\tUpper"
                flag=False
             if self._data[key].lower is not None:
                lval = str(self._data[key].lower())
             else:
                lval = "-Infinity"
             val = str(self._data[key].body())
             if self._data[key].upper is not None:
                uval = str(self._data[key].upper())
             else:
                uval = "Infinity"
             print >>ostream, "%s  %s :\t%s\t%s\t%s" % (
                              prefix, str(key), lval, val, uval )
           if flag:
                print >>ostream, prefix+"  None active"



class SOSConstraint(ConstraintBase):
    """
    Represents an SOS-n constraint.

    Usage:
    model.C1 = SOSConstraint(
                             [...],
                             var=VAR,
                             [set=SET OR index=SET],
                             [sos=N OR level=N]
                             )
        [...] Any number of sets used to index SET
        VAR   The set of variables making up the SOS. Indexed by SET.
        SET   The set used to index VAR. SET is optionally indexed by
              the [...] sets. If SET is not specified, VAR is indexed
              over the set(s) it was defined with.
        N     This constraint is an SOS-N constraint. Defaults to 1.

    Example:

      model = Model()
      model.A = Set()
      model.B = Set(A)
      model.X = Set(B)

      model.C1 = SOSConstraint(model.A, var=model.X, set=model.B, sos=1)

    This constraint actually creates one SOS-1 constraint for each
    element of model.A (e.g., if |A| == N, there are N constraints).
    In each constraint, model.X is indexed by the elements of
    model.D[a], where 'a' is the current index of model.A.

      model = Model()
      model.A = Set()
      model.X = Var(model.A)

      model.C2 = SOSConstraint(var=model.X, sos=2)

    This produces exactly one SOS-2 constraint using all the variables
    in model.X.
    """


    alias("SOSConstraint", "SOS constraint expressions in a model.")

    def __init__(self, *args, **kwargs):
        if kwargs.pop('_deep_copying', None):
            # Hack for Python 2.4 compatibility
            # Deep copy will copy all items as necessary, so no need to
            # complete parsing
            return

        name = kwargs.get('name', 'unknown')

        # Get the 'var' parameter
        sosVars = kwargs.pop('var', None)

        # Get the 'set' or 'index' parameters
        if 'set' in kwargs and 'index' in kwargs:
            raise TypeError, "Specify only one of 'set' and 'index' -- " \
                  "they are equivalent parameters"
        sosSet = kwargs.pop('set', None)
        sosSet = kwargs.pop('index', sosSet)

        # Get the 'sos' or 'level' parameters
        if 'sos' in kwargs and 'index' in kwargs:
            raise TypeError, "Specify only one of 'sos' and 'level' -- " \
                  "they are equivalent parameters"
        sosLevel = kwargs.pop('sos', None)
        sosLevel = kwargs.pop('level', sosLevel)

        # Make sure sosLevel has been set
        if sosLevel is None:
            raise TypeError, "SOSConstraint() requires that either the " \
                  "'sos' or 'level' keyword arguments be set to indicate " \
                  "the type of SOS."

        # Make sure we have a variable
        if sosVars is None:
            raise TypeError, "SOSConstraint() requires the 'var' keyword " \
                  "be specified"

        # Find the default sets for sosVars if sosSets is None
        if sosSet is None:
            sosSet = sosVars.index()

        # Construct parents
        kwargs['ctype'] = kwargs.get('ctype', SOSConstraint)
        ConstraintBase.__init__(self, *args, **kwargs)

        # Set member attributes
        self._sosVars = sosVars
        self._sosSet = sosSet
        self._sosLevel = sosLevel

        # TODO figure out why exactly the code expects this to be defined
        # likely due to Numericvalue
        self.domain = None

        # TODO should variables be ordered?

    def construct(self, *args, **kwds):
        """
        A quick hack to call add after data has been loaded. construct
        doesn't actually need to do anything.
        """
        self.add()

    def add(self, *args):
        """
        Mimics Constraint.add, but is only used to alert preprocessors
        to the existence of the SOS variables.

        Ignores all arguments passed to it.
        """

        # self._data is a ConstraintData object, which has a member
        # .body.  .body needs to have a 3-tuple of expressions
        # containing the variables that are referenced by this
        # constraint. We only use one index, None. I have no
        # particular reason to use None, it just seems consistent with
        # what Constraint objects do.

        # For simplicity, we sum over the variables.

        vars = self.sos_vars()

        expr = sum(vars[i] for i in vars._index)

        self._data[None] = ConstraintData(name=create_name(self.name, None))
        self._data[None].body = expr

    def sos_level(self):
        """ Return n, where this class is an SOS-n constraint """
        return self._sosLevel

    def sos_vars(self):
        """ Return the variables in the SOS """
        return self._sosVars

    def sos_set(self):
        """ Return the set used to index the variables """
        return self._sosSet

    def sos_set_set(self):
        """ Return the sets used to index the sets indexing the variables """
        return self._index

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "Type="+str(self._sosLevel)
        print >>ostream, "\tVariable: "+self._sosVars.name
        print >>ostream, "\tIndices: ",
        for i in self._sosSet.value:
           print >>ostream, str(i)+" ",
        print >>ostream, ""
