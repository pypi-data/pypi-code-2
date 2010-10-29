#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction, Var, Constraint, Objective
import pyutilib.component.core

ignore = set(['"', "'", '`'])
remap = {}
# Remap as underscores
remap['-']='_'
remap['_']='_'
remap[' ']='_'
remap['(']='['
remap['{']='['
remap[')']=']'
remap['}']=']'
# Remap as Q+ASCII-Dec
remap['!']='_Q33_'
remap['#']='_Q35_'
remap['$']='_Q36_'
remap['%']='_Q37_'
remap['&']='_Q38_'
remap['*']='_Q42_'
remap['+']='_Q43_'
#remap[',']='_Q44_'
remap['.']='_Q46_'
remap['/']='_Q47_'
remap[';']='_Q59_'
remap['<']='_Q60_'
remap['=']='_Q61_'
remap['>']='_Q62_'
remap['?']='_Q63_'
remap['@']='_Q63_'
remap['\\']='_Q92_'
remap['^']='_Q94_'
remap['|']='_Q124_'
remap['~']='_Q126_'

class GenericVarLabelsPresolver(pyutilib.component.core.SingletonPlugin):
    """
    This plugin changes variables names to generate a label that
    can be used in LP/MILP file formats.
    """

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "generic_varlabels"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 1000

    def _name_fix(self, name):
        global ignore
        global remap
        tmp=""
        for c in name:
            if c in remap:
                tmp += remap[c]
            elif not c in ignore:
                tmp += c
        return tmp

    def preprocess(self, model):
        """
        The main routine to perform the preprocess
        """
        #
        # This creates labels for all variables, not just the ones used
        # in this instance.  This is useful when interrogating unused 
        # variables.
        #
        # NOTES: in theory - unless model components are added on-the-fly - 
        #        this routine only needs to be executed once. unfortunately, we
        #        don't track new components (yet), so we have to preprocess
        #        just in case the model was updated. however, if there is 
        #        already a label attribute there, don't re-generate it, as
        #        the name fix takes a non-trivial amount of time. the 
        #        underlying assumption is that component names won't change,
        #        which is a good one.
        #
        active_variables = model.active_components(Var)
        for var in active_variables.values():
            for index, var_value in var._varval.iteritems():
#                if not hasattr(var_value, "label"):
                   var_value.label = self._name_fix(var_value.name)
                   model._name_varmap[var_value.label] = var_value
        active_constraints = model.active_components(Constraint)
        for con in active_constraints.values():
            for index, constraint_data in con._data.iteritems():
#                if not hasattr(constraint_data, "label"):
                   constraint_data.label = self._name_fix(constraint_data.name)
                   model._name_conmap[constraint_data.label ] = constraint_data
        active_objectives = model.active_components(Objective)
        for obj in active_objectives.values():
            for index, objective_data in obj._data.iteritems():
#                if not hasattr(objective_data, "label"):
                   objective_data.label = self._name_fix(objective_data.name)
                   model._name_objmap[objective_data.label ] = objective_data
        return model
            
