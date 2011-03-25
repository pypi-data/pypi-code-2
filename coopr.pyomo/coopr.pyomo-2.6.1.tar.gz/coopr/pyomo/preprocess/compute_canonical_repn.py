#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

#
# Note: this leaves the trivial constraints in the model
#

import sys
import logging
import pyutilib.component.core
from coopr.pyomo.base import Constraint, Objective
from coopr.pyomo.base import IPyomoPresolver, IPyomoPresolveAction
import coopr.pyomo.expr 

# NOTE: The idea of this module should be generaized. there are two key 
#       functionalities: computing a version of the expression tree in
#       preparation for output and identification of trivial constraints.

class ComputeCanonicalRepn(pyutilib.component.core.SingletonPlugin):
    """
    This plugin computes the canonical representation for 
    all objectives and constraints linear terms.
    """

    # all modifications are in-place, i.e., components of the
    # input instance are modified.

    pyutilib.component.core.implements(IPyomoPresolveAction)

    def __init__(self, **kwds):
        kwds['name'] = "compute_canonical_repn"
        pyutilib.component.core.Plugin.__init__(self, **kwds)

    def rank(self):
        return 10000

    def preprocess(self, model):
        """
        The main routine to perform the preprocess
        """

        if getattr(model,'skip_canonical_repn',False):
            return model
        
        #
        # Objectives
        #
        active_objectives = model.active_components(Objective)
        for key, obj in active_objectives.iteritems():
            # number of objective indicies with non-trivial expressions
            num_nontrivial = 0
            
            for ondx, objective_data in obj._data.iteritems():
                if not objective_data.active:
                    continue
                if objective_data.expr is None:
                    raise ValueError, "No expression has been defined for objective %s" % str(key)
                
                try:
                    objective_data.repn = coopr.pyomo.expr.generate_canonical_repn(objective_data.expr, context=obj, key=ondx)
                except Exception, err:
                    logging.getLogger('coopr.pyomo').error\
                        ( "exception generating a canonical representation for objective %s (index %s): %s" \
                              % (str(key), str(ondx), str(err)) )
                    raise
                if not coopr.pyomo.expr.is_constant(objective_data.repn):
                    num_nontrivial += 1
                    
            if num_nontrivial == 0:
                obj.trivial = True
            else:
                obj.trivial = False
                
        #
        # Constraints
        #
        active_constraints = model.active_components(Constraint)
        for key, constraint in active_constraints.iteritems():

            # number of constraint indicies with non-trivial bodies
            num_nontrivial = 0
            
            for index, constraint_data in constraint._data.iteritems():

                if not constraint_data.active:
                    continue

                if constraint_data.lin_body is not None:
                   # if we already have the linear encoding of the constraint body, skip canonical expression 
                   # generation but we still need to assess constraint triviality.
                   if not coopr.pyomo.expr.is_linear_expression_constant(constraint_data.lin_body):
                      num_nontrivial += 1          
                   continue

                if constraint_data.body is None:
                    raise ValueError, "No expression has been defined for the body of constraint %s, index=%s" % (str(key), str(index))
                
                try:
                    constraint_data.repn = coopr.pyomo.expr.generate_canonical_repn(constraint_data.body, context=constraint, key=index)
                except Exception:
                    logging.getLogger('coopr.pyomo').error\
                        ( "exception generating a canonical representation for constraint %s (index %s)" \
                              % (str(key), str(index)) )
                    raise
                if not coopr.pyomo.expr.is_constant(constraint_data.repn):
                    num_nontrivial += 1
                    
            if num_nontrivial == 0:
                constraint.trivial = True
            else:
                constraint.trivial = False
        #
        # Return modified instance
        #
        return model

