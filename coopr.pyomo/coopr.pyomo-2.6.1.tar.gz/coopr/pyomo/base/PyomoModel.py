#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________

__all__ = ['Model', 'ConcreteModel', 'AbstractModel']

import array
import copy
import logging
import re
import sys
import traceback

from plugin import *
from numvalue import *

import pyutilib.component.core
from pyutilib.math import *
from pyutilib.misc import quote_split, tuplize, Container, PauseGC

from coopr.opt import ProblemFormat, ResultsFormat, guess_format
from coopr.opt.results import SolutionMap
from coopr.pyomo.base.var import _VarValue, VarStatus, Var
from coopr.pyomo.base.constraint import ConstraintData
from coopr.pyomo.base.set_types import *
import coopr.opt
from PyomoModelData import ModelData

from block import Block
from sets import Set

try:
   from pympler.muppy import tracker
   pympler_available = True
except ImportError:
   pympler_available = False

logger = logging.getLogger('coopr.pyomo')

class Model(Block):
    """
    An optimization model.  By default, this defers construction of components
    until data is loaded.
    """

    pyutilib.component.core.alias("Model", 'Model objects can be used as a '  \
                                  'component of other models.')

    preprocessor_ep = pyutilib.component.core.ExtensionPoint(IPyomoPresolver)

    def __init__ ( self, name='unknown', _deprecate=True, **kwargs ):
        """Constructor"""
        if _deprecate:
           msg = "Using the 'Model' class is deprecated.  Please use the "    \
                 "'AbstractModel' class instead."
           logger.warning( msg )

        Block.__init__(self, ctype=Model)

        # cached name-based object lookup data to facilitate fast solution loading.
        # handled by the various objects (the items in the map) during construction.
        self._name_varmap={} # maps labels to _VarValue objects
        self._name_conmap={} # maps labels to ConstraintData objects
        self._name_objmap={} # maps labels to ObjectiveData objects

        self.name=name
        self.tmpctr=0
        self._varctr=0
        self._preprocessors = ["simple_preprocessor"]
        #
        # Dictionaries that map from id to Variable/Constraints
        #
        self._var = {}
        self._con = {}
        self._obj = {}
        #
        # Model statistics
        #
        self.statistics = Container()
        #
        # We make the default behavior of has_capabilities to lie and return
        # True. We do this to allow the richest output formats when no
        # solver is specified. These capabilities _will_ be overwritten
        # when a solver is specified.
        #
        # We define _tempTrue since using self.has_capability = lambda x: True
        # causes pickling errors.
        #
        self.has_capability = _tempTrue

    def nvariables(self):
        return self.statistics.number_of_variables

    def variable(self, name):
        if isinstance(name,basestring):
            return self._name_varmap[name]
        else:
            return self._var[name-1]

    def has_discrete_variables(self):

       variables = self.active_components(Var)
       for variable_name, variable in variables.items():
          if isinstance(variable.domain, IntegerSet) or isinstance(variable.domain, BooleanSet):
             return True
       return False


    def variables(self):
        return self._name_varmap

    def nconstraints(self):
        return self.statistics.number_of_constraints

    def constraint(self, name):
        if isinstance(name,basestring):
            return self._name_conmap[name]
        else:
            return self._con[name-1]

    def constraints(self):
        return self._name_conmap

    def nobjectives(self):
        return self.statistics.number_of_objectives

    def objective(self, name):
        if isinstance(name,basestring):
            return self._name_objmap[name]
        else:
            return self._obj[name-1]

    def objectives(self):
        return self._name_objmap

    def num_used_variables(self):
        return len(self._var)

    def valid_problem_types(self):
        return [ProblemFormat.pyomo]

    def create(self, filename=None, name=None, namespace=None, namespaces=None, preprocess=True, simplify=None, profile_memory=0):
        """
        Create a concrete instance of this Model, possibly using data
        read in from a file.
        """

        if simplify is not None:
           print """
WARNING: The 'simplify' argument to PyomoModel.create() has been deprecated.
     Please remove references from your code.
"""
        if self._defer_construction:
            instance = self.clone()

            if namespaces is None:
                instance.load(filename, namespaces=[namespace], profile_memory=profile_memory)
            else:
                instance.load(filename, namespaces=namespaces, profile_memory=profile_memory)
        else:
            instance = self
        if preprocess is True:

           if (pympler_available is True) and (profile_memory >= 2):
              memory_tracker = tracker.SummaryTracker()
              memory_tracker.create_summary()

           instance.preprocess()

           if (pympler_available is True) and (profile_memory >= 2):
              print "Objects created during instance preprocessing:"
              memory_tracker.print_diff()

        if not name is None:
            instance.name=name
        return instance

    def clone(self):
        """Create a copy of this model"""

        for name in self.components:
            #print 'y',name
            #print 'z', type(self.components[name])
            self.components[name].model = None

        instance = copy.deepcopy(self)

        for name in self.components:
            self.components[name].model = self
        for name in instance.components:
            instance.components[name].model = instance
        return instance

    def reset(self):
        for name in self.components:
            self.components[name].reset()

    def preprocess(self):
        """Apply the preprocess plugins defined by the user"""
        suspend_gc = PauseGC()
        for item in self._preprocessors:
            self = Model.preprocessor_ep.service(item).preprocess(self)

    def solution(selfNone):
        """Return the solution"""
        soln = []
        for i in range(len(self._var)):
            soln.append( self._var[i].value )
        return soln

    def update_results(self, results):
        for i in xrange(len(results.solution)):
            soln = results.solution(i+1)
            #
            # Variables
            #
            vars = SolutionMap()
            flag=False
            for name in soln.variable.keys():
                flag=True
                entry = soln.variable[name]
                # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT variable
                if name == "ONE_VAR_CONSTANT":
                    continue
                # translate the name first if there is a variable map associated
                # with the input solution.
                if results.symbol_map is not None:
                    name = results.symbol_map.get(name, name)
                if name not in self._name_varmap:
                    msg = "Variable name '%s' is not in model '%s'.  Valid "      \
                        'variable names: %s'
                    raise KeyError, msg % (
                          name, self.name, str(self._name_varmap.keys()) )
                var_value = self._name_varmap[name]
                entry.id = var_value.id
                vars.declare(name)
                dict.__setitem__(vars,name, entry)
            if flag:
                dict.__setitem__(soln, 'Variable', vars)
            #
            # Constraints
            #
            cons = SolutionMap()
            flag=False
            for name in soln.constraint.keys():
                flag=True
                entry = soln.constraint[name]
                if results.symbol_map is not None:
                    name = results.symbol_map.get(name, name)
                if name not in self._name_conmap:
                    msg = "Constraint name '%s' is not in model '%s'.  Valid "      \
                        'constraint names: %s'
                    raise KeyError, msg % (
                          name, self.name, str(self._name_conmap.keys()) )
                con_value = self._name_conmap[name]
                entry.id = con_value.id
                cons.declare(name)
                dict.__setitem__(cons,name, entry)
            if flag:
                dict.__setitem__(soln, 'Constraint', cons)
            #
            # Objectives
            #
            objs = SolutionMap()
            flag=False
            for name in soln.objective.keys():
                flag=True
                entry = soln.objective[name]
                if results.symbol_map is not None:
                    name = results.symbol_map.get(name, name)
                if not name in self._name_objmap:
                    msg = "Objective name '%s' is not in model '%s'.  Valid "      \
                        'objective names: %s'
                    raise KeyError, msg % (
                          name, self.name, str(self._name_objmap.keys()) )
                obj_value = self._name_objmap[name]
                entry.id = obj_value.id
                objs.declare(name)
                dict.__setitem__(objs,name, entry)
            if flag:
                dict.__setitem__(soln, 'Objective', objs)
        
    def load(self, arg, namespaces=[None], simplify=None, profile_memory=0):
        """ Load the model with data from a file or a Solution object """

        if simplify is not None:
           print """
WARNING: The 'simplify' argument to PyomoModel.load() has been deprecated.
     Please remove references from your code.
"""

        if arg is None or type(arg) is str:
           self._load_model_data(ModelData(filename=arg,model=self), namespaces, profile_memory=profile_memory)
           return True
        elif type(arg) is ModelData:
           self._load_model_data(arg, namespaces, profile_memory=profile_memory)
           return True
        elif type(arg) is coopr.opt.SolverResults:
           # if the solver status not one of either OK or Warning, then error.
           if (arg.solver.status != coopr.opt.SolverStatus.ok) and \
              (arg.solver.status != coopr.opt.SolverStatus.warning):
               msg = 'Cannot load a SolverResults object with bad status: %s'
               raise ValueError, msg % str( arg.solver.status )

           # but if there is a warning, print out a warning, as someone should
           # probably take a look!
           if (arg.solver.status == coopr.opt.SolverStatus.warning):
               print 'WARNING - Loading a SolverResults object with a '       \
                     'warning status'

           if len(arg.solution) > 0:
              self._load_solution(arg.solution(0),symbol_map=arg.symbol_map)
              return True
           else:
              return False
        elif type(arg) is coopr.opt.Solution:
           self._load_solution(arg)
           return True
        elif type(arg) in (tuple, list):
           self._load_solution(arg)
           return True
        else:
            msg = "Cannot load model with object of type '%s'"
            raise ValueError, msg % str( type(arg) )

    def store_info(self, results):
        """ Store model information into a SolverResults object """
        results.problem.name = self.name

        stat_keys = (
          'number_of_variables',
          'number_of_binary_variables',
          'number_of_integer_variables',
          'number_of_continuous_variables',
          'number_of_constraints',
          'number_of_objectives'
        )

        for key in stat_keys:
            results.problem.__dict__[key] = self.statistics.__dict__[key]

    def _tuplize(self, data, setobj):
        if data is None:            #pragma:nocover
           return None
        if setobj.dimen == 1:
           return data
        ans = {}
        for key in data:
          if type(data[key][0]) is tuple:
             return data
          ans[key] = tuplize(data[key], setobj.dimen, setobj.name)
        return ans

    def _load_model_data(self, modeldata, namespaces, **kwds):
        """
        Load declarations from a ModelData object.
        """

        # As we are primarily generating objects here (and acyclic ones
        # at that), there is no need to run the GC until the entire
        # model is created.  Simple reference-counting should be
        # sufficient to keep memory use under control.
        suspend_gc = PauseGC()

        profile_memory = kwds.get('profile_memory', 0)

        # for pretty-printing summaries - unlike the standard
        # method in the pympler summary module, the tracker
        # doesn't print 0-byte entries to pad out the limit.
        if (pympler_available is True) and (profile_memory >= 2):
           memory_tracker = tracker.SummaryTracker()

        # Do some error checking
        for namespace in namespaces:
            if not namespace is None and not namespace in modeldata._data:
                msg = "Cannot access undefined namespace: '%s'"
                raise IOError, msg % namespace

        # Initialize each component in order.
        components = [key for key in self.components]

        for component_name in components:

            if (pympler_available is True) and (profile_memory >= 2):
               memory_tracker.create_summary()

            if self.components[component_name].type() is Model:
                continue
            declaration = self.components[component_name]
            if component_name in modeldata._default.keys():
                if declaration.type() is Set:
                    declaration.set_default(self._tuplize(modeldata._default[component_name], declaration))
                else:
                    declaration.set_default(modeldata._default[component_name])
            data = None

            for namespace in namespaces:
                if component_name in modeldata._data.get(namespace,{}).keys():
                    if declaration.type() is Set:
                        data = self._tuplize(modeldata._data[namespace][component_name],
                                             declaration)
                    else:
                        data = modeldata._data[namespace][component_name]
                if not data is None:
                    break

            if __debug__:
                if logger.isEnabledFor(logging.DEBUG):
                    msg = "About to generate '%s' with data: %s"
                    print msg % ( declaration.name, str(data) )
                    self.pprint()

            try:
                declaration.construct(data)
            except:
                logger.error("constructing declaration '%s' from data=%s failed", 
                             str(declaration.name), str(data).strip() )
                raise

            if (pympler_available is True) and (profile_memory >= 2):
               print "Objects created during construction of component "+component_name+":"
               memory_tracker.print_diff()

    def _load_solution(self, soln, symbol_map=None):
        """
        Load a solution.
        """
        # Load list or tuple into the variables, based on their order
        if type(soln) in (list, tuple):
            if len(soln) != len(self._var):
                msg = 'Attempting to load a list/tuple solution into a '      \
                      'model, but its length is %d while the model has %d '   \
                      'variables' % (len(soln), len(self._var))
                raise ValueError, msg % ( len(soln), len(self._var) )
            for i in range(len(soln)):
                self._var[i].value = soln[i]
            return
        #
        # Load variable data
        #
        for name, entry in soln.variable.iteritems():

            # NOTE: the following is a hack, to handle the ONE_VAR_CONSTANT
            #    variable that is necessary for the objective constant-offset
            #    terms.  Probably should create a dummy variable in the model
            #    map at the same time the objective expression is being
            #    constructed.

          if name != "ONE_VAR_CONSTANT":

             # translate the name first if there is a variable map associated
             # with the input solution.
             if symbol_map is not None:
                name = symbol_map.get(name, name)
             if name not in self._name_varmap:
                msg = "Variable name '%s' is not in model '%s'.  Valid "      \
                      'variable names: %s'
                raise KeyError, msg % (
                          name, self.name, str(self._name_varmap.keys()) )

             if not isinstance(self._name_varmap[name],_VarValue):
                 msg = "Variable '%s' in model '%s' is type %s"
                 raise TypeError, msg % (
                     name, self.name, str(type(self._name_varmap[name])) )

             if self._name_varmap[name].fixed is True:
                 msg = "Variable '%s' in model '%s' is currently fixed - new" \
                       ' value is not expected in solution'
                 raise TypeError, msg % ( name, self.name )

             if self._name_varmap[name].status is not VarStatus.used:
                 msg = "Variable '%s' in model '%s' is not currently used - no" \
                       ' value is expected in solution'
                 raise TypeError, msg % ( name, self.name )

             var_value = self._name_varmap[name]
             for _key in entry.keys():
                key = _key[0].lower() + _key[1:]
                if key == 'value':
                    var_value.value = entry.value
                elif not key == 'id':
                    var_value.setattrvalue(key, getattr(entry, _key))
        #
        # Load constraint data
        #
        for name,entry in soln.constraint.iteritems():
             #
             # This is a hack - see above.
             #
             if name.endswith('ONE_VAR_CONSTANT'):
                continue
             if symbol_map is not None:
                name = symbol_map.get(name, name)
             #
             # This is a hack.  Is there a standard convention for constraint
             # names that we can apply to all data formats?
             #
             if name[0:2] == 'c_':
                _name = name[4:-1]
             else:
                _name = name

             if _name not in self._name_conmap:
                msg = "Constraint name '%s' is not in model '%s'.  Valid "    \
                      'constraint names: %s'
                raise KeyError, msg % (
                              _name, self.name, str(self._name_conmap.keys()) )

             if not isinstance(self._name_conmap[_name],ConstraintData):
                 msg = "Constraint '%s' in model '%s' is type %s"
                 raise TypeError, msg % (
                        name, self.name, str(type(self._name_conmap[_name])) )

             constraint_data = self._name_conmap[_name]
             for _key in entry.keys():
                key = _key[0].lower() + _key[1:]
                if key == 'value':
                    constraint_data.value = entry.value
                elif not key == 'id':
                    setattr(constraint_data, key, getattr(entry, _key))

    def write(self,filename=None,format=ProblemFormat.cpxlp):
        """
        Write the model to a file, with a given format.
        """
        if format is None and not filename is None:
            #
            # Guess the format
            #
            format = guess_format(filename)
        #print "X",str(format),coopr.opt.WriterFactory.services()
        problem_writer = coopr.opt.WriterFactory(format)
        if problem_writer is None:
            msg = "Cannot write model in format '%s': no model writer "      \
                  'registered for that format'
            raise ValueError, msg % str(format)

        (fname, symbol_map) = problem_writer(self, filename)
        if __debug__:
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Writing model '%s' to file '%s' with format %s", self.name, str(fname), str(format))
        return fname, symbol_map

    def to_standard_form(self):
        """
        Produces a standard-form representation of the model. Returns
        the coefficient matrix (A), the cost vector (c), and the
        constraint vector (b), where the 'standard form' problem is

        min/max c'x
        s.t.    Ax = b
                x >= 0

        All three returned values are instances of the array.array
        class, and store Python floats (C doubles).
        """

        from coopr.pyomo.expr import generate_canonical_repn


        # We first need to create an map of all variables to their column
        # number
        colID = {}
        ID2name = {}
        id = 0
        tmp = self.variables().keys()
        tmp.sort()

        for v in tmp:
            colID[v] = id
            ID2name[id] = v
            id += 1

        # First we go through the constraints and introduce slack and excess
        # variables to eliminate inequality constraints
        #
        # N.B. Structure heirarchy:
        #
        # active_components: {class: {attr_name: object}}
        # object -> Constraint: ._data: {ndx: ConstraintData}
        # ConstraintData: .lower, .body, .upper
        #
        # So, altogether, we access a lower bound via
        #
        # model.active_components()[Constraint]['con_name']['index'].lower
        #
        # {le,ge,eq}Constraints are
        # {constraint_name: {index: {variable_or_none: coefficient}} objects
        # that represent each constraint. None in the innermost dictionary
        # represents the constant term.
        #
        # i.e.
        #
        # min  x1 + 2*x2 +          x4
        # s.t. x1                         = 1
        #           x2   + 3*x3          <= -1
        #      x1 +                 x4   >= 3
        #      x1 + 2*x2 +      +   3*x4 >= 0
        #
        #
        # would be represented as (modulo the names of the variables,
        # constraints, and indices)
        #
        # eqConstraints = {'c1': {None: {'x1':1, None:-1}}}
        # leConstraints = {'c2': {None: {'x2':1, 'x3':3, None:1}}}
        # geConstraints = {'c3': {None: {'x1':1, 'x4':1, None:-3}},
        #                  'c4': {None: {'x1':1, 'x2':2, 'x4':1, None:0}}}
        #
        # Note the we have the luxury of dealing only with linear terms.
        leConstraints = {}
        geConstraints = {}
        eqConstraints = {}
        objectives = {}
        # For each registered component
        for c in self.active_components():

            # Get all subclasses of ConstraintBase
            if issubclass(c, ConstraintBase):
                cons = self.active_components(c)

                # Get the name of the constraint, and the constraint set itself
                for con_set_name in cons:
                    con_set = cons[con_set_name]

                    # For each indexed constraint in the constraint set
                    for ndx in con_set._data:
                        con = con_set._data[ndx]

                        # Process the body
                        terms = self._process_canonical_repn(
                            generate_canonical_repn(con.body))

                        # Process the bounds of the constraint
                        if con._equality:
                            # Equality constraint, only check lower bound
                            lb = self._process_canonical_repn(
                                generate_canonical_repn(con.lower))

                            # Update terms
                            for k in lb:
                                v = lb[k]
                                if k in terms:
                                    terms[k] -= v
                                else:
                                    terms[k] = -v

                            # Add constraint to equality constraints
                            eqConstraints[(con_set_name, ndx)] = terms
                        else:

                            # Process upper bounds (<= constraints)
                            if con.upper is not None:
                                # Less than or equal to constraint
                                tmp = dict(terms)

                                ub = self._process_canonical_repn(
                                    generate_canonical_repn(con.upper))

                                # Update terms
                                for k in ub:
                                    if k in terms:
                                        tmp[k] -= ub[k]
                                    else:
                                        tmp[k] = -ub[k]

                                # Add constraint to less than or equal to
                                # constraints
                                leConstraints[(con_set_name, ndx)] = tmp

                            # Process lower bounds (>= constraints)
                            if con.lower is not None:
                                # Less than or equal to constraint
                                tmp = dict(terms)

                                lb = self._process_canonical_repn(
                                    generate_canonical_repn(con.lower))

                                # Update terms
                                for k in lb:
                                    if k in terms:
                                        tmp[k] -= lb[k]
                                    else:
                                        tmp[k] = -lb[k]

                                # Add constraint to less than or equal to
                                # constraints
                                geConstraints[(con_set_name, ndx)] = tmp
            elif issubclass(c, Objective):
                # Process objectives
                objs = self.active_components(c)

                # Get the name of the objective, and the objective set itself
                for obj_set_name in objs:
                    obj_set = objs[obj_set_name]

                    # For each indexed objective in the objective set
                    for ndx in obj_set._data:
                        obj = obj_set._data[ndx]
                        # Process the objective
                        terms = self._process_canonical_repn(
                            generate_canonical_repn(obj.expr))

                        objectives[(obj_set_name, ndx)] = terms


        # We now have all the constraints. Add a slack variable for every
        # <= constraint and an excess variable for every >= constraint.
        nSlack = len(leConstraints)
        nExcess = len(geConstraints)

        nConstraints = len(leConstraints) + len(geConstraints) + \
                       len(eqConstraints)
        nVariables = len(colID) + nSlack + nExcess
        nRegVariables = len(colID)

        # Make the arrays
        coefficients = array.array("d", [0]*nConstraints*nVariables)
        constraints = array.array("d", [0]*nConstraints)
        costs = array.array("d", [0]*nVariables)

        # Populate the coefficient matrix
        constraintID = 0

        # Add less than or equal to constraints
        for ndx in leConstraints:
            con = leConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            # Add the slack
            coefficients[constraintID*nVariables + nRegVariables + \
                        constraintID] = 1
            constraintID += 1

        # Add greater than or equal to constraints
        for ndx in geConstraints:
            con = geConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            # Add the slack
            coefficients[constraintID*nVariables + nRegVariables + \
                        constraintID] = -1
            constraintID += 1

        # Add equality constraints
        for ndx in eqConstraints:
            con = eqConstraints[ndx]
            for termKey in con:
                coef = con[termKey]

                if termKey is None:
                    # Constraint coefficient
                    constraints[constraintID] = -coef
                else:
                    # Variable coefficient
                    col = colID[termKey]
                    coefficients[constraintID*nVariables + col] = coef

            constraintID += 1

        # Determine cost coefficients
        for obj_name in objectives:
            obj = objectives[obj_name]
            for var in obj:
                costs[colID[var]] = obj[var]

        # Print the model
        #
        # The goal is to print
        #
        #         var1   var2   var3   ...
        #       +--                     --+
        #       | cost1  cost2  cost3  ...|
        #       +--                     --+
        #       +--                     --+ +-- --+
        # con1  | coef11 coef12 coef13 ...| | eq1 |
        # con2  | coef21 coef22 coef23 ...| | eq2 |
        # con2  | coef31 coef32 coef33 ...| | eq3 |
        #  .    |   .      .      .   .   | |  .  |
        #  .    |   .      .      .    .  | |  .  |
        #  .    |   .      .      .     . | |  .  |

        constraintPadding = 2
        numFmt = "% 1.4f"
        altFmt = "% 1.1g"
        maxColWidth = max(len(numFmt % 0.0), len(altFmt % 0.0))
        maxConstraintColWidth = max(len(numFmt % 0.0), len(altFmt % 0.0))

        # Generate constraint names
        maxConNameLen = 0
        conNames = []
        for name in leConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)
        for name in geConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)
        for name in eqConstraints:
            strName = str(name)
            if len(strName) > maxConNameLen:
                maxConNameLen = len(strName)
            conNames.append(strName)

        # Generate the variable names
        varNames = [None]*len(colID)
        for name in colID:
            tmp_name = " " + name
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames[colID[name]] = tmp_name
        for i in xrange(0, nSlack):
            tmp_name = " _slack_%i" % i
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames.append(tmp_name)
        for i in xrange(0, nExcess):
            tmp_name = " _excess_%i" % i
            if len(tmp_name) > maxColWidth:
                maxColWidth = len(tmp_name)
            varNames.append(tmp_name)

        # Variable names
        line = " "*maxConNameLen + (" "*constraintPadding) + " "
        for col in xrange(0, nVariables):
            # Format entry
            token = varNames[col]

            # Pad with trailing whitespace
            token += " "*(maxColWidth - len(token))

            # Add to line
            line += " " + token + " "
        print line

        # Cost vector
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+"
        line = " "*maxConNameLen + (" "*constraintPadding) + "|"
        for col in xrange(0, nVariables):
            # Format entry
            token = numFmt % costs[col]
            if len(token) > maxColWidth:
                token = altFmt % costs[col]

            # Pad with trailing whitespace
            token += " "*(maxColWidth - len(token))

            # Add to line
            line += " " + token + " "
        line += "|"
        print line
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+"

        # Constraints
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+" + \
              (" "*constraintPadding) + "+--" + \
              (" "*(maxConstraintColWidth-1)) + "--+"
        for row in xrange(0, nConstraints):
            # Print constraint name
            line = conNames[row] + (" "*constraintPadding) + (" "*(maxConNameLen - len(conNames[row]))) + "|"

            # Print each coefficient
            for col in xrange(0, nVariables):
                # Format entry
                token = numFmt % coefficients[nVariables*row + col]
                if len(token) > maxColWidth:
                    token = altFmt % coefficients[nVariables*row + col]

                # Pad with trailing whitespace
                token += " "*(maxColWidth - len(token))

                # Add to line
                line += " " + token + " "

            line += "|" + (" "*constraintPadding) + "|"

            # Add constraint vector
            token = numFmt % constraints[row]
            if len(token) > maxConstraintColWidth:
                token = altFmt % constraints[row]

            # Pad with trailing whitespace
            token += " "*(maxConstraintColWidth - len(token))

            line += " " + token + "  |"
            print line
        print " "*maxConNameLen + (" "*constraintPadding) + "+--" + \
              " "*((maxColWidth+2)*nVariables - 4) + "--+" + \
              (" "*constraintPadding) + "+--" + (" "*(maxConstraintColWidth-1))\
              + "--+"

        return (coefficients, costs, constraints)

    def _process_canonical_repn(self, expr):
        """
        Returns a dictionary of {var_name_or_None: coef} values
        """

        terms = {}

        # Get the variables from the canonical representation
        vars = expr.pop(-1, {})

        # Find the linear terms
        linear = expr.pop(1, {})
        for k in linear:
            # FrozeDicts don't support (k, v)-style iteration
            v = linear[k]

            # There's exactly 1 variable in each term
            terms[vars[k.keys()[0]].label] = v

        # Get the constant term, if present
        const = expr.pop(0, {})
        if None in const:
            terms[None] = const[None]

        if len(expr) != 0:
            raise TypeError, "Nonlinear terms in expression"

        return terms


def _tempTrue(x):
    """
    Defined to return True to all inquiries
    """
    return True


class ConcreteModel(Model):
    """
    A concrete optimization model that does not defer construction of
    components.
    """

    def __init__(self, *args, **kwds):
        kwds['_deprecate'] = False
        Model.__init__(self, *args, **kwds)
        self._defer_construction=False

    pyutilib.component.core.alias("ConcreteModel", 'A concrete optimization model that '\
              'does not defer construction of components.')

class AbstractModel(Model):
    """
    An abstract optimization model that defers construction of
    components.
    """

    def __init__(self, *args, **kwds):
        kwds['_deprecate'] = False
        Model.__init__(self, *args, **kwds)
        self._defer_construction=True

    pyutilib.component.core.alias("AbstractModel", 'An abstract optimization model that '\
              'defers construction of components.')

