#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________


import pyutilib.component.core
from coopr.pyomo.base import expr, Constraint, Objective, SOSConstraint
from coopr.pyomo.base.var import  _VarValue, VarStatus, _VarArray, _VarBase, Var
from coopr.pyomo.base.numvalue import NumericConstant
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction


class IdentifyVariablesPresolver(pyutilib.component.core.SingletonPlugin):
    """
    This plugin processes a Pyomo Model instance to define
    the order of variables and to categorize constraints.
    """

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "identify_variables"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1

    #
    # Scan through a linearly encoded expression body to identify variables.
    #
    def _identify_variables_in_linear_encoding(self, encoding, model):

       for coefficient, var in encoding[1]:

          if var.fixed_value():

             continue

          elif isinstance(var, _VarValue):

             var.status = VarStatus.used
             if var.id in model._var:
                continue
             var.id = self.var_count
             model._var[self.var_count] = var
             self.var_count += 1

          elif isinstance(var, _VarBase):

             var.status = VarStatus.used
             tmp = var.as_numeric()
             if var is exp:
                 raise ValueError, "Variable %s appears in an expression without an index, but this variable is an indexed value." % var.name
             if tmp.id in model._var:
                continue
             tmp.id = self.var_count
             model._var[self.var_count] = tmp
             self.var_count += 1            

          else:

             raise RuntimeError, "Unknown object of type="+str(type(var))+" encountered in linear expression encoding"

    #
    # Recursively work through an expression (tree) to identify variables.
    #
    def _identify_variables_in_expression(self, exp, model):

        try:
            if exp.fixed_value():
                return
        except AttributeError, e:
            # Likely caused by a constraint or an objective failing
            # to return a value. Let
            msg = str(e)

            if isinstance(exp, _VarArray):
                msg += "\n    Have you properly indexed '%s'?" % str(exp)
            else:
                msg += "\n    Do all constraints and objectives return a " + \
                       "value?"
            msg += " type="+str(type(exp))
            raise AttributeError, msg
                
        #
        # Product Expressions store stuff differently
        #
        if type(exp) is expr._ProductExpression:
            for arg in exp._numerator:
                self._identify_variables_in_expression(arg, model)
            for arg in exp._denominator:
                self._identify_variables_in_expression(arg, model)
        #
        # Expression
        #
        elif isinstance(exp,expr.Expression):
            for arg in exp._args:
                self._identify_variables_in_expression(arg, model)
        #
        # Variable Value
        #
        elif isinstance(exp,_VarValue):
            exp.status = VarStatus.used
            if exp.id in model._var:
                return
            exp.id = self.var_count
            model._var[self.var_count] = exp
            self.var_count += 1
        #
        # Variable Base
        #
        elif isinstance(exp,_VarBase):
            exp.status = VarStatus.used
            tmp = exp.as_numeric()
            if tmp is exp:
                raise ValueError, "Variable %s appears in an expression without an index, but this variable is an indexed value." % exp.name
            if tmp.id in model._var:
                return
            tmp.id = self.var_count
            model._var[self.var_count] = tmp
            self.var_count += 1            
        #
        # If not a constant, then this is an error
        #
        elif exp is not None:
            raise ValueError, "Unexpected expression type in identify_variables: " + str(type(exp))+" "+str(exp)

    #
    # this pre-processor computes a number of attributes of model components, in 
    # addition to models themselves. for VarValue, ConstraintData, and ObjectiveData,
    # the routine assigns the "id" attribute. in addition, for VarValues, the routine
    # sets the "status" attribute - to used or unused, depending on whether it appears
    # in an active constraint/objective. on the Model object, the routine populates
    # the "statistics" (variable/constraint/objective counts) attribute, and builds 
    # the _var, _con, and _obj dictionaries of a Model, which map the id attributes
    # to the respective VarValue, ConstraintData, or ObjectiveData object.
    #
    # NOTE: if variables are fixed, then this preprocessor will flag them as unused
    #       and consequently not create entries for them in the model _var map. 
    #

    def preprocess(self,model):
        """
        The main routine to perform the preprocess
        """

        active_variables = model.active_components(Var)
        active_constraints = model.active_components(Constraint)
        active_objectives = model.active_components(Objective)

        active_constraints.update(model.active_components(SOSConstraint))

        self.var_count=0
        self.constraint_count=0
        self.objective_count=0
        
        model.statistics.number_of_binary_variables = 0
        model.statistics.number_of_integer_variables = 0
        model.statistics.number_of_continuous_variables = 0

        #
        # Reset the _var map. Failing to reset can cause problems in cloned
        # instances.
        #
        model._var = {}
        
        #
        # Until proven otherwise, all variables are unused.
        #
        for var in active_variables.values():
            for var_value in var._varval.values():
                var_value.status = VarStatus.unused
                var_value.id = -1

        #
        # Call the appropriate identify_variables to find the variables that 
        # are actively used in the objective and constraints.
        #
        for name, objective in active_objectives.iteritems():
            for index, objective_data in objective._data.iteritems():
                if not objective_data.active:
                    continue
                try:
                    self._identify_variables_in_expression(objective_data.expr, model)
                except ValueError, err:
                    raise ValueError, "Problem processing objective %s (index %s): %s" % (str(name), str(index), str(err))

                objective_data.id = self.objective_count
                model._obj[self.objective_count] = objective_data
                self.objective_count += 1

        for name, constraint in active_constraints.iteritems():
            for index, constraint_data in constraint._data.iteritems():
                if not constraint_data.active:
                    continue
                try:
                    if constraint_data.lin_body is not None:
                       self._identify_variables_in_linear_encoding(constraint_data.lin_body, model)               
                    else:
                       self._identify_variables_in_expression(constraint_data.body, model)
                except ValueError, err:
                    raise ValueError, "Problem processing constraint %s (index %s): %s" % (str(name), str(index), str(err))
                constraint_data.id = self.constraint_count
                model._con[self.constraint_count] = constraint_data
                self.constraint_count += 1

        #
        # count the number of variables in each type category.
        # we don't do this within the _identify_variables_in_expression function
        # because the variable type is owned by the "parent"
        # variable, and the interrogation cost for variable type
        # is comparatively expensive - we don't want to do it for
        # each variable value.
        #
        for var in active_variables.values():
            model.statistics.number_of_binary_variables += len(var.binary_keys())
            model.statistics.number_of_integer_variables += len(var.integer_keys())
            model.statistics.number_of_continuous_variables += len(var.continuous_keys())

        #
        # assign the model statistics
        #

        model.statistics.number_of_variables = self.var_count
        model.statistics.number_of_constraints = self.constraint_count
        model.statistics.number_of_objectives = self.objective_count

        return model

