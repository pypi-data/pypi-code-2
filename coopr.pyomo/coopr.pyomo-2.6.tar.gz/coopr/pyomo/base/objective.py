__all__ = ['Objective']

import sys
import logging

from expr import *
from indexed_component import IndexedComponent
from numtypes import *
from numvalue import *
from numvalue import create_name
from label import *
from pyutilib.component.core import alias
from sets import _BaseSet, _SetContainer, _ProductSet
from var import Var, _VarValue, _VarArray, _VarElement
import pyutilib.math
import pyutilib.misc

from component import Component
from set_types import *
from sets import _SetContainer

logger = logging.getLogger('coopr.pyomo')


class ObjectiveData(NumericValue):

    __slots__ = ['obj', 'expr', 'label', 'id', 'active', 'repn', 'ampl_repn']

    def __init__(self, expr=None, name=None, obj=None):
        NumericValue.__init__(self,name=name,domain=Reals)

        self.expr = expr
        self.obj = obj

        # the label is a modification of the input name, with certain symbols
        # that are typically problematic for solver input files re-mapped (e.g., 
        # curly braces) to more friendly symbols. create a default label right
        # away - it can be modified if a particular solver needs it.
        # self.label = None (is set one way or another via the following method)
        self.sync_label()

        self.id = -1

        self.active = True

        self.repn = None
        self.ampl_repn = None

    def __getstate__(self):
       result = NumericValue.__getstate__(self)
       for i in ObjectiveData.__slots__:
          result[i] = getattr(self, i)
       return result        

    def sync_label(self):
        if self.name is not None:
            self.label = label_from_name(self.name)
            if (self.obj is not None) and (self.obj.model is not None):
                self.obj.model._name_objmap[self.label] = self
        else:
            self.label = None

    def __call__(self, exception=True):
        if self.expr is None:
            return None
        return self.expr()

    def polynomial_degree(self):
        if self.expr is None:
            return None
        return self.expr.polynomial_degree()

    def activate(self):
        self.active=True

    def deactivate(self):
        self.active=False


class Objective(IndexedComponent, NumericValue):
    """An object that defines a objective expression"""

    alias('Objective', 'Expressions that are minimized or maximized in a '    \
          'model.')

    def __init__(self, *args, **kwargs):
        """Construct an objective expression with rule to construct the
           expression
        """
        tkwargs = {'ctype':Objective}
        IndexedComponent.__init__(self, *args, **tkwargs)

        self._data = {}
        if args == ():
            self._data[None] = ObjectiveData(obj=self)
        else:
            for i in args:
                if not ( isinstance(i, _SetContainer) ):
                    msg  = 'Invalid argument.  Objective expects arguments of '
                    msg += "type 'Set', not type '%s'"
                    raise TypeError, msg % str( type(i).__name__ )

        # this is a hack for now; we eventually want a
        # "QuadraticObjective" class.
        self._quad_subexpr = None

        tmpname  = kwargs.pop('name', 'unknown')
        tmpsense = kwargs.pop('sense', minimize )
        tmprule  = kwargs.pop('rule', None )
        tmprule  = kwargs.pop('expr', tmprule )
        self.doc = kwargs.pop('doc', None )
        self._no_rule_init = kwargs.get('noruleinit', None )

        # _no_rule_init is a flag specified by the user to indicate that no
        # construction rule will be specified, and that constraints will be
        # explicitly added by the user. set via the "noruleinit" keyword. value
        # doesn't matter, as long as it isn't "None".

        if ( kwargs ): # if dict not empty, there's an error.  Let user know.
            msg = "Creating constraint '%s': unknown option(s)\n\t%s"
            msg = msg % ( tmpname, ', '.join(kwargs.keys()) )
            raise ValueError, msg

        NumericValue.__init__( self, name=tmpname )        

        if None in self._data:
            self._data[None].name = self.name
            self._data[None].sync_label()

        self.sense   = tmpsense
        self.rule    = tmprule
        self.trivial = False # True if all objective indicies have trivial expressions.
        self._constructed = False

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
            if self._data[None].expr is None:
                return None
            return self._data[None].expr()
        if exception:
            msg = 'Cannot compute the value of an array of objectives'
            raise ValueError, msg

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

    def __getitem__(self,ndx):
        """This method returns a ObjectiveData object.  This object can be
           coerced to a numeric value using the value() function, or using
           explicity coercion with float().
        """
        if ndx in self._data:
           return self._data[ndx]
        msg = "Unknown index in objective '%s': %s"
        raise KeyError, msg % ( self.name, str(ndx) )

    def __iter__(self):
        return self._data.keys().__iter__()
        #return self._index.__iter__()

    def _apply_rule(self,arg,ndx):
        tmp = self.rule(*arg)
        if tmp is None:
           return None
        if type(tmp) in [bool,int,long,float]:
           return NumericConstant(value=tmp)
        return tmp


    def is_minimizing ( self ):
        return minimize == self.sense


    def construct(self, data=None):
        if __debug__:
            logger.debug("Constructing objective %s", self.name)
        if (self._no_rule_init is not None) and (self.rule is not None):
            msg = 'WARNING: noruleinit keyword is being used in conjunction ' \
                  "with rule keyword for objective '%s'; defaulting to "      \
                  'rule-based construction'
            print msg % self.name
        if self.rule is None:
           if self._no_rule_init is None:
               msg = 'WARNING: No construction rule or expression specified ' \
                     "for objective '%s'"
               print msg % self.name
           return
        if self._constructed:
            return
        self._constructed=True
        #
        if isinstance(self.rule,Expression) or isinstance(self.rule,_VarValue):
            if None in self._index or len(self._index) == 0 or self._index[None] is None:
                self._data[None].expr = self.rule
            else:
                msg = 'Cannot define multiple indices in an objective with a' \
                      'single expression'
                raise IndexError, msg
        #
        elif self.rule is not None:
           if self._ndim==0:
              tmp = self._apply_rule((self.model,),None)
              if tmp is not None and not (type(tmp) in (int,long,float)       \
                                          and tmp == 0):
                 self._data[None].expr = tmp
              self._data[None].label = label_from_name(self.name)
           else:
              _name=self.name
              for val in self._index:
                if type(val) is tuple:
                   tmp = list(val)
                else:
                   tmp = [val]
                tmp.append(self.model)
                tmp = tuple(tmp)
                tmp = self._apply_rule(tmp,val)
                if tmp is not None and not (type(tmp) in (int,long,float)     \
                                            and tmp == 0):
                    self._data[val] = ObjectiveData(expr=tmp,
                                                   name=create_name(_name,val), obj=self)
           #self._index = self._data.keys()
        #
        if None in self._data:
            self._data[None].label = label_from_name(self.name)
        #
        # update the parent model (if any) name->constraint map.
        #
        if self.model is not None:
           for objective_data in self._data.itervalues():
              self.model._name_objmap[objective_data.label] = objective_data

    def pprint(self, ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, "  ",self.name,":",
        print >>ostream, "\tSize="+str(len(self._data.keys())),
        if isinstance(self._index,_BaseSet):
           print >>ostream, "\tIndex=",self._index.name
        else:
           print >>ostream,""
        for key in self._data:
          if not self._data[key].expr is None:
                print >>ostream, "\t",
                self._data[key].expr.pprint(ostream)
                print >>ostream, ""
        if self._quad_subexpr is not None:
           print >>ostream, "\tQuadratic sub-expression: ",
           self._quad_subexpr.pprint(ostream)
           print >>ostream, ""

    def display(self, prefix="", ostream=None):
        if ostream is None:
           ostream = sys.stdout
        print >>ostream, prefix+"Objective "+self.name,":",
        print >>ostream, "  Size="+str(len(self))
        if None in self._data:
            if self._data[None].expr is None:
                val = 'none'
            else:
                val = pyutilib.misc.format_io(self._data[None].expr(exception=False))
            print >>ostream, '%s  Value=%s' % (prefix, val)
        else:
           for key in self._data:
             if not self._data[key].active:
                continue
             val = self._data[key].expr(exception=False)
             print >>ostream, prefix+"  "+str(key)+" : "+str(val)
