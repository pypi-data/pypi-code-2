# dlw - base energy model - begin Jan 2009
# feb09, convert to multiple arcs between two nodes

#
# Imports (i.e., magical incantations)
#

import sys
import os
from os.path import abspath, dirname
sys.path.insert(0, dirname(dirname(dirname(dirname(abspath(__file__))))))
from coopr.pyomo import *

#
# Model
#

# According to DLW the model name should be mnemonic,  but short
model = Model()
model.name = "Electrical Grid Operation Model - Basic Version"

#
# Parameters
#

# demand profile time segments \mathcal{H}
model.ProfileSlots = Set()

# network nodes \mathcal{N}
model.Nodes = Set()

# arcs
model.Arcs = Set()
model.ArcsIn = Set(model.Nodes, within=model.Arcs)
model.ArcsOut = Set(model.Nodes, within=model.Arcs)

"""
in order to allow multiple arcs between nodes, the arcsin/arcsout sets are no longer derived; they are input
# derived data
def arcs_in_populate_rule(i, model):
   # Set() doesn't work, but we think it should. sets.Set() makes it function correctly, for magical reasons.
   ans = sets.Set()
   for a in model.Arcs:
      if a[1] == i:
         ans = ans.add((a[0],a[1]))
   return ans

model.ArcsIn = Set(model.Nodes, within=model.Arcs, initialize=arcs_in_populate_rule)

def arcs_out_populate_rule(i, model):
   # Set() doesn't work, but we think it should. sets.Set() makes it function correctly, for magical reasons.
   ans = sets.Set()
   for a in model.Arcs:
      if a[0] == i:
         ans = ans.add((a[0],a[1]))
      # REMOVE THIS HACK WHEN WE FIGURE OUT WHY ADDING MORE THAN ONE ELEMENT TO A SET CHOKES
      return ans
   return ans

model.ArcsOut = Set(model.Nodes, within=model.Arcs, initialize=arcs_out_populate_rule)

end of commented-out arcsin/arcsout section
"""

# I'm not sure this is a good way...
model.ProductionModeMasterList = Set()

#see page 159 of AMPL 2nd Edition (and model.F in the pyomo data.py example)
# modes of production at a node \mathcal{M}(i), i \in \mathcal{N}
model.ProductionModes = Set(model.Nodes, within=model.ProductionModeMasterList);

# hours with the the time bucket for a demand profile slot
model.SlotHours = Param(model.ProfileSlots, within=PositiveReals)

# cost per hour of the production modes
model.HourlyCosts = Param(model.ProductionModeMasterList, within=PositiveReals)

# demands for each node.
model.NodeDemands = Param(model.Nodes, model.ProfileSlots, within=PositiveReals, default=0.00001)

# capacity for each production mode
model.ModeCapacity = Param(model.ProductionModeMasterList, within=PositiveReals)

# capacity for each arc
model.ArcCapacity = Param(model.Arcs, within=PositiveReals)

# fraction of capacity lost.
model.LineLossFraction = Param(model.Arcs, within=PositiveReals, default=0.05)

#
# Variables
#

# production quantities
# note: the upper bounds would depend on the production mode
model.x = Var(model.Nodes, model.ProductionModeMasterList, model.ProfileSlots, bounds=(0.0, None))

# the flow variables.
model.y = Var(model.Arcs, model.ProfileSlots, bounds=(0.0, None))

#
# Constraints
#

def limited_production_rule(i, m, h, model):
   if m in model.ProductionModes[i]:
      return (0.0, model.x[i,m,h], model.ModeCapacity[m])
   else:
      return None   

model.EnforceLimitedProduction = Constraint(model.Nodes, model.ProductionModeMasterList, model.ProfileSlots, rule=limited_production_rule)

# we don't like the tuple notation, or at least it should be made consistent with AMPL.
def limit_arc_capacity(a, h, model):
   return (0.0, model.y[a, h], model.ArcCapacity[a])

model.EnforceArcCapacities = Constraint(model.Arcs, model.ProfileSlots, rule=limit_arc_capacity)

def flow_balance_constraint(i, h, model):
   flow_balance_right = model.NodeDemands[i, h]
   for a in model.ArcsOut[i]:
      flow_balance_right = flow_balance_right + model.y[a, h]
   flow_balance_left = 0.0
   for m in model.ProductionModes[i]:
      flow_balance_left = flow_balance_left + model.x[i, m, h]
   for a in model.ArcsIn[i]:
      flow_balance_left = flow_balance_left + ((1.0 - model.LineLossFraction[a]) * model.y[a, h])
   return (0.0, flow_balance_left - flow_balance_right, 0.0)

model.EnforceFlowBalance = Constraint(model.Nodes, model.ProfileSlots, rule=flow_balance_constraint)

#
# Objective
#

def production_cost_rule(model):
    ans = 0.0
    for i in model.Nodes:
        for m in model.ProductionModes[i]:
            for h in model.ProfileSlots:
                ans = ans + model.SlotHours[h] * model.HourlyCosts[m] * model.x[i,m,h]
    return ans
model.Production_Cost_Objective = Objective(rule=production_cost_rule, sense=minimize)
