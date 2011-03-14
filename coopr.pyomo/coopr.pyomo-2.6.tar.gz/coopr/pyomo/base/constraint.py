#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Constraint', 'SOSConstraint', 'ConstraintBase', 'ConstraintList']

import sys
import logging

from expr import *
from indexed_component import IndexedComponent
from numtypes import *
from numvalue import *
from numvalue import create_name
from label import *
from pyutilib.component.core import alias
from sets import _BaseSet, _SetContainer, _ProductSet, Set
from var import Var, _VarValue, _VarArray, _VarElement
from objective import Objective
import pyutilib.math
import pyutilib.misc

from component import Component
from set_types import *
from sets import _SetContainer

logger = logging.getLogger('coopr.pyomo')


class ConstraintBase(IndexedComponent):
    """
    Abstract base class for all constraint types. Keeps track of how many
    constraint objects are in existence.
    """

    alias("ConstraintBase", "Abstract base class for all model constraints")

    # The number of explicit constraints declared.
    _nExplicitConstraints = 0

    def __init__(self, *args, **kwargs):
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

    __slots__ = ('con','label','id','active','_equality','lower',
                 'lower_ineq_strict','lin_body','body','upper',
                 'upper_ineq_strict','repn','ampl_repn','dual')

    def __init__(self, name, con=None):

        NumericValue.__init__(self,name=name,domain=Reals)

        self.con = con

        # the label is a modification of the input name, with certain symbols
        # that are typically problematic for solver input files re-mapped (e.g., 
        # curly braces) to more friendly symbols. create a default label right
        # away - it can be modified if a particular solver needs it.
        # self.label = None (is set one way or another via the following method)
        self.sync_label()

        # TBD: Document where this gets populated.
        self.id = None

        # TBD: Mirroring the variable class, the constraint data class should really "know" its index and its parent constraint.

        # is this variable an active component of the current model?
        self.active = True
        
        self._equality = False
        self.lower = None
        self.lower_ineq_strict = None
        self.lin_body = None # a linear compilation of the source expressions tree.
        self.body = None # an expression tree encoding of the constraint body. if None, an alternative representation (e.g., lin_body) will be != None.
        self.upper = None
        self.upper_ineq_strict = None

        self.repn = None
        self.ampl_repn = None

        self.dual = None

    def __getstate__(self):
       result = NumericValue.__getstate__(self)
       for i in ConstraintData.__slots__:
          result[i] = getattr(self, i)
       return result        

    def sync_label(self):
        if self.name is not None:
            self.label = label_from_name(self.name)
            if (self.con is not None) and (self.con.model is not None):
                self.con.model._name_conmap[self.label] = self
        else:
            self.label = None

    def __call__(self, exception=True):
        if self.body is None:
            return None
        return self.body()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Constraint(ConstraintBase, NumericValue):
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

    def __getstate__(self):
       result = NumericValue.__getstate__(self)
       for key,value in self.__dict__.iteritems():
          result[key]=value
       return result            

    def clear(self):
        self._data = {}

    def __call__(self, exception=True):
        if len(self._data) == 0:
            return None
        if None in self._data:
            if self._data[None].body is None:
                return None
            return value(self._data[None].body)
        if exception:
            msg = 'Cannot compute the value of an array of constraints'
            raise ValueError, msg


    def construct(self, data=None):

        # cache the debug generation flag, to avoid the expense of 
        # calling isEnabledFor() for each index - this is far too
        # expensive an operation to perform deep in a loop. the only
        # potential down-side is that the debug logging is either
        # disabled or enabled globally for the duration of this 
        # method invocation - which doesn't seem like much of
        # (if any) limitation in practice.
        generate_debug_messages = (__debug__ is True) and (logger.isEnabledFor(logging.DEBUG) is True)

        if generate_debug_messages is True:
            logger.debug("Constructing constraint %s",self.name)

        if (self._no_rule_init is not None) and (self.rule is not None):
            logger.warn("noruleinit keyword is being used in conjunction with "
                        "rule keyword for constraint '%s'; defaulting to "
                        "rule-based construction.", self.name)
        if self.rule is None:
            if self._no_rule_init is None:
                logger.warn("No construction rule or expression specified for "
                            "constraint '%s'", self.name)
            return
        if self._constructed:
            return
        self._constructed=True

        #
        # Local variables for code optimization
        #
        _self_rule = self.rule
        _self_model = self.model

        #
        if None in self._index:
            if len(self._index) != 1:
                raise IndexError, "Internal error: constructing constraint "\
                    "with both None and Index set"
            if generate_debug_messages:
                logger.debug("  Constructing single constraint (index=None)")
            if isinstance(_self_rule,Expression):
                expr = _self_rule
            else:
                expr = _self_rule(_self_model)
            if expr is not None:
                self.add(None, expr)
        else:
            if isinstance(_self_rule,Expression):
                raise IndexError, "Cannot define multiple indices in a " \
                    "constraint with a single expression"
            for index in self._index:
                if generate_debug_messages:
                    logger.debug("  Constructing constraint index "+str(index))
                if type(index) is tuple:
                    expr = _self_rule(*( index + (_self_model,) ))
                else:
                    expr = _self_rule(index, _self_model)
                if expr is not None:
                    self.add(index, expr)

    def add(self, index, expr):

        # index: the constraint index (should probably be renamed)
        # expr: the constraint expression

        #
        # Ignore an 'empty' constraint
        #
        if expr is None:
            return

        expr_type = type(expr)

        # Local variables to optimize runtime performance
        #
        conData = ConstraintData(name=create_name(self.name,index), con=self)
        conData.lower_ineq_strict = conData.upper_ineq_strict = False

        if expr_type is tuple: # or expr_type is list:
            #
            # Form equality expression
            #
            if len(expr) == 2:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                conData._equality = True
                if arg1 is None or arg1.is_constant():
                    conData.lower = conData.upper = arg1
                    conData.body = arg0
                elif arg0 is None or arg0.is_constant():
                    conData.lower = conData.upper = arg0
                    conData.body = arg1
                else:
                    conData.lower = conData.upper = NumericConstant(value=0)
                    conData.body = arg0 - arg1
            #
            # Form inequality expression
            #
            elif len(expr) == 3:
                arg0 = expr[0]
                if arg0 is not None:
                    arg0 = as_numeric(arg0)
                    if not arg0.is_constant():
                        msg = "Constraint '%s' found a 3-tuple (lower, " \
                              "expression, upper) but the lower value was "\
                              "non-constant"
                        raise ValueError, msg % (conData.name,)

                arg1 = expr[1]
                if arg1 is not None:
                    arg1 = as_numeric(arg1)

                arg2 = expr[2]
                if arg2 is not None:
                    arg2 = as_numeric(arg2)
                    if not arg2.is_constant():
                        msg = "Constraint '%s' found a 3-tuple (lower, " \
                              "expression, upper) but the upper value was "\
                              "non-constant"
                        raise ValueError, msg % (conData.name,)

                conData.lower = arg0
                conData.body  = arg1
                conData.upper = arg2
            else:
                msg = "Constructor rule for constraint '%s' returned a tuple" \
                      ' of length %d.  Expecting a tuple of length 2 or 3:\n' \
                      'Equality:   (left, right)\n' \
                      'Inequality: (lower, expression, upper)'
                raise ValueError, msg % ( self.name, len(expr) )

            relational_expr = False
        else:
            try:
                relational_expr = expr.is_relational()
                if not relational_expr:
                    msg = "Constraint '%s' does not have a proper value.  " \
                          "Found '%s'\nExpecting a tuple or equation.  " \
                          "Examples:\n" \
                          "    summation( model.costs ) == model.income\n" \
                          "    (0, model.price[ item ], 50)"
                    raise ValueError, msg % ( conData.name, str(expr) )
            except:
                msg = "Constraint '%s' does not have a proper value.  " \
                      "Found '%s'\nExpecting a tuple or equation.  " \
                      "Examples:\n" \
                      "    summation( model.costs ) == model.income\n" \
                      "    (0, model.price[ item ], 50)"
                raise ValueError, msg % ( conData.name, str(expr) )
                
        if relational_expr:
            if expr_type is _EqualityExpression:
                # Equality expression: only 2 arguments!
                conData._equality = True
                if expr._args[1].is_constant():
                    conData.lower = conData.upper = expr._args[1]
                    conData.body = expr._args[0]
                elif expr._args[0].is_constant():
                    conData.lower = conData.upper = expr._args[0]
                    conData.body = expr._args[1]
                else:
                    conData.lower = conData.upper = NumericConstant(value=0)
                    conData.body = expr._args[0] - expr._args[1]
            else:
                # Inequality expression: 2 or 3 arguments
                if len(expr._args) == 3:
                    if not expr._args[0].is_constant():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the lower bound was non-constant"
                        raise ValueError, msg % (conData.name,)
                    if not expr._args[2].is_constant():
                        msg = "Constraint '%s' found a double-sided "\
                              "inequality expression (lower <= expression "\
                              "<= upper) but the upper bound was non-constant"
                        raise ValueError, msg % (conData.name,)
                    conData.lower = expr._args[0]
                    conData.body  = expr._args[1]
                    conData.upper = expr._args[2]
                    conData.lower_ineq_strict = expr._strict[0]
                    conData.upper_ineq_strict = expr._strict[1]
                else:
                    if expr._args[1].is_constant():
                        conData.lower = None
                        conData.body  = expr._args[0]
                        conData.upper = expr._args[1]
                        conData.upper_ineq_strict = expr._strict[0]
                    elif expr._args[0].is_constant():
                        conData.lower = expr._args[0]
                        conData.body  = expr._args[1]
                        conData.upper = None
                        conData.lower_ineq_strict = expr._strict[0]
                    else:
                        conData.lower = None
                        conData.body  = expr._args[0] - expr._args[1]
                        conData.upper = NumericConstant(value=0)
                        conData.upper_ineq_strict = expr._strict[0]

        #
        # Replace numeric bound values with a NumericConstant object,
        # and reset the values to 'None' if they are 'infinite'
        #
        if conData.lower is not None:
            val = conData.lower()
            if not pyutilib.math.is_finite(val):
                if val > 0:
                    msg = "Constraint '%s' created with a +Inf lower bound"
                    raise ValueError, msg % ( conData.name, )
                conData.lower = None
                conData.lower_ineq_strict = False
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric lower bound"
                raise ValueError, msg % ( conData.name, )
        if conData.upper is not None:
            val = conData.upper()
            if not pyutilib.math.is_finite(val):
                if val < 0:
                    msg = "Constraint '%s' created with a -Inf upper bound"
                    raise ValueError, msg % ( conData.name, )
                conData.upper = None
                conData.upper_ineq_strict = False
            elif bool(val > 0) == bool(val <= 0):
                msg = "Constraint '%s' created with a non-numeric upper bound"
                raise ValueError, msg % ( conData.name, )

        # Error check, to ensure that we don't have a constraint that
        # doesn't depend on any variables / parameters 
        #
        # TBD: This is an expensive test (is_constant() is recursive).
        # The pre-coopr-2.5 version of this test was basically never
        # executed (just looked for int, float, etc.)  It is not clear
        # that running this debugging test is even worth it [JDS, 28 Feb 2011].
        #
        #if conData.body.is_constant():
        #    feasible = True
        #    value = conData.body()
        #    if conData.lower is not None:
        #        if conData.lower_ineq_strict:
        #            feasible = feasible and (conData.lower() < value)
        #        else:
        #            feasible = feasible and (conData.lower() <= value)
        #    if conData.upper is not None:
        #        if conData.upper_ineq_strict:
        #            feasible = feasible and (value < conData.upper())
        #        else:
        #            feasible = feasible and (value < conData.upper())
        #    if feasible:
        #        logger.warn("Constraint '%s' has a constant constant body.")
        #    else:
        #        logger.error("Constraint '%s' has an constant infeasible "
        #                     "constant body.")

        # Error check, to ensure that we don't have an equality constraint with
        # 'infinite' RHS
        #
        if conData._equality:
            if conData.lower != conData.upper: #pragma:nocover
                msg = "Equality constraint '%s' has non-equal lower and "\
                      "upper bounds (this is indicitive of a SERIOUS "\
                      "internal error in Pyomo)."
                raise RuntimeError, msg % self.name
            if conData.lower is None:
                msg = "Equality constraint '%s' defined with non-finite term"
                raise ValueError, msg % self.name

        #
        # hook up the constraint data object to the parent constraint.
        #
        self._data[index] = conData

        #
        # update the parent model (if any) name->constraint map.
        #
        if self.model is not None:
           self.model._name_conmap[conData.label] = conData


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
             if self._data[val].lower.is_expression():
                self._data[val].lower.pprint(ostream)
             else:
                print >>ostream, str(self._data[val].lower)
          else:
             print >>ostream, "\t\t-Inf"
          if self._data[val].lower_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].body is not None:
             print >>ostream, "\t\t",
             if self._data[val].body.is_expression():
                self._data[val].body.pprint(ostream)
             else:
                print >>ostream, str(self._data[val].body)
          #else:                         #pragma:nocover
             #raise ValueError, "Unexpected empty constraint body"
          if self._data[val].upper_ineq_strict:
             print >>ostream, "\t\t<"
          else:
             print >>ostream, "\t\t<="
          if self._data[val].upper is not None:
             print >>ostream, "\t\t",
             if self._data[val].upper.is_expression():
                self._data[val].upper.pprint(ostream)
             else:
                print >>ostream, str(self._data[val].upper)
          elif self._data[val]._equality:
             print >>ostream, "\t\t",
             if self._data[val].lower.is_expression():
                self._data[val].lower.pprint(ostream)
             else:
                print >>ostream, str(self._data[val].lower)
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



class ConstraintList(Constraint):
    """
    A constraint component that represents a list of constraints.  Constraints can
    be indexed by their index, but when they are added an index value is not specified.
    """

    alias("ConstraintList", "A list of constraints in a model.")

    def __init__(self, *args, **kwargs):
        if len(args) > 0:
            raise ValueError, "Cannot specify indices for a ConstraintList object"

        # Construct parents
        kwargs['ctype'] = kwargs.get('ctype', ConstraintList)
        self._hidden_index = Set()
        self._nconstraints = 0
        targs = [self._hidden_index]
        Constraint.__init__(self, *targs, **kwargs)
        #self._no_rule_init = kwargs.pop('noruleinit', None )
        #tmprule = kwargs.pop('rule', None )
        #tmprule = kwargs.pop('expr', tmprule )

    def construct(self, *args, **kwds):
        self._hidden_index.construct()
        Constraint.construct(self, *args, **kwds)

    def construct(self, data=None):
        #
        if __debug__:
            logger.debug("Constructing constraint %s",self.name)
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
        while True:
            val = self._nconstraints + 1
            if __debug__:
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug("   Constructing constraint index "+str(val))
            tmp=(val, self.model)
            expr = _self_rule(*tmp)
            if expr is None or (type(expr) in (int, long, float) and expr == 0):
                break
            self.add(expr)

    def add(self, *args):
        self._nconstraints += 1
        targs = [self._nconstraints] + list(args)
        Constraint.add(self, *targs)



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

      model = AbstractModel()
      model.A = Set()
      model.B = Set(A)
      model.X = Set(B)

      model.C1 = SOSConstraint(model.A, var=model.X, set=model.B, sos=1)

    This constraint actually creates one SOS-1 constraint for each
    element of model.A (e.g., if |A| == N, there are N constraints).
    In each constraint, model.X is indexed by the elements of
    model.D[a], where 'a' is the current index of model.A.

      model = AbstractModel()
      model.A = Set()
      model.X = Var(model.A)

      model.C2 = SOSConstraint(var=model.X, sos=2)

    This produces exactly one SOS-2 constraint using all the variables
    in model.X.
    """


    alias("SOSConstraint", "SOS constraint expressions in a model.")

    def __init__(self, *args, **kwargs):
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

        self._data[None] = ConstraintData(name=create_name(self.name, None), con=self)
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
