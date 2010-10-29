# fbv - Chile rules!
# dlw - base forest model - begin April 2009
# mnr - base forest model - revised May 1, 2009 - changed the notation of parameters to match those in paper.

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
model = Model()
model.name = "Forest Management Base Model"

#
# Implementation Sets (not in paper, used to make it happen)
# general nodes (not in paper)
model.Nodes = Set()

#
# Sets
#

# time Horizon \mathcal{T}
model.Times = Set(ordered=True)

# network nodes \mathcal{O}
model.OriginNodes = Set(within=model.Nodes)

# intersection nodes
model.IntersectionNodes = Set(within=model.Nodes)

# wood exit nodes
model.ExitNodes = Set(within=model.Nodes)

# harvest cells \mathcal{H}
model.HarvestCells = Set()

# harvest cells for origin o \mathcal{H}_o
model.HCellsForOrigin = Set(model.OriginNodes, within=model.HarvestCells)

# existing roads
model.ExistingRoads = Set(within=model.Nodes*model.Nodes) 

# potential roads
model.PotentialRoads = Set(within=model.Nodes*model.Nodes)

# Roads declaring
#model.AllRoads = model.ExistingRoads & model.PotentialRoads
model.AllRoads = Set(within=model.Nodes*model.Nodes)

# derived set
def aplus_arc_set_rule(v, model):
   return  [(i, j) for (i, j) in model.AllRoads if j == v]
model.Aplus = Set(model.Nodes, within=model.AllRoads, rule=aplus_arc_set_rule)

# derived set
def aminus_arc_set_rule(v, model):
   return  [(i, j) for (i, j) in model.AllRoads if i == v]
model.Aminus = Set(model.Nodes, within=model.AllRoads, rule=aminus_arc_set_rule)

#
# Deterministic Parameters
#

# productivity of cell h if it is harvested in period t
model.a = Param(model.HarvestCells, model.Times)

# Area of cell h to be harvested
model.A = Param(model.HarvestCells)

# flow capacity (smallest big M) 
def Umax_init(model):
   return (sum([model.a[h, t] * model.A[h] for h in model.HarvestCells for t in model.Times])/2)()
model.Umax = Param(initialize=Umax_init)

# harvesting cost of one hectare of cell h in time t
model.P = Param(model.HarvestCells, model.Times)

# unit Production cost at origin o in time t
model.Q = Param(model.OriginNodes, model.Times)

# construction cost of one road in arc (k,l) in time t
model.C = Param(model.PotentialRoads, model.Times, default=0.0)

# unit transport cost through arc (k,l) in time t
model.D = Param(model.AllRoads, model.Times)

#
# Stochastic Parameters
#

# sale price at exit s in time period t
model.R = Param(model.ExitNodes, model.Times)

# upper and lower bounds on wood supplied
model.Zlb = Param(model.Times)
model.Zub = Param(model.Times)

#
# Variables
#

# If cell h is harvested in period t
model.delta = Var(model.HarvestCells, model.Times, domain=Boolean)

# If road in arc (k,l) is built in period t
model.gamma = Var(model.PotentialRoads, model.Times, domain=Boolean)

# Flow of wood thransported through arc (k,l)
model.f = Var(model.AllRoads, model.Times, domain=NonNegativeReals)

# Supply of wood at exit s in period t
model.z = Var(model.ExitNodes, model.Times, domain=NonNegativeReals)

# Declared when changing the program for stochastics
model.AnoProfit = Var(model.Times)

#
# Constraints
#

# flow balance at origin nodes
def origin_flow_bal(o, t, model):
   ans1 = sum([model.a[h, t] * model.A[h] * model.delta[h, t] for h in model.HCellsForOrigin[o]])
   ans2 = sum([model.f[k, o, t] for (k, o) in model.Aplus[o]])
   ans3 = sum([model.f[o, k, t] for (o, k) in model.Aminus[o]])
   return (ans1 + ans2 - ans3) == 0.0

model.EnforceOriginFlowBalance = Constraint(model.OriginNodes, model.Times, rule=origin_flow_bal)

# flow balance at intersection nodes
def intersection_flow_bal(j, t, model):
   return (sum([model.f[k, j, t] for (k, j) in model.Aplus[j]]) - sum([model.f[j, k, t] for (j, k) in model.Aminus[j]])) == 0.0

model.EnforceIntersectionFlowBalance = Constraint(model.IntersectionNodes, model.Times, rule=intersection_flow_bal)

# flow balance at destination nodes
def destination_flow_bal(e, t, model):
   return (model.z[e, t] - sum([model.f[k, e, t] for (k, e) in model.Aplus[e]]) + sum([model.f[e, k, t] for (e, k) in model.Aminus[e]])) == 0.0

model.EnforceDestinationFlowBalance = Constraint(model.ExitNodes, model.Times, rule=destination_flow_bal)

# explicit divergence or supply equals demand or no inventory between periods
def divergence_flow_bal(t, model):
   return (sum([model.z[e, t] for e in model.ExitNodes]) - sum([model.a[h, t] * model.A[h] * model.delta[h, t] for h in model.HarvestCells])) == 0.0

model.EnforceDivergenceFlowBalance = Constraint(model.Times, rule=divergence_flow_bal)

# Wood Production Bounds
def wood_prod_bounds(t, model):
   return (model.Zlb[t], sum([model.z[e, t] for e in model.ExitNodes]), model.Zub[t])

model.EnforceWoodProductionBounds = Constraint(model.Times, rule=wood_prod_bounds)

# potential roads flow capacity 1 
def pot_road_flow_capacity(k, l, t, model):
	return (None, model.f[k, l, t] - sum([model.Umax * model.gamma[k, l, tau] for tau in model.Times if tau <= t]), 0.0)

model.EnforcePotentialRoadFlowCap = Constraint(model.PotentialRoads, model.Times, rule=pot_road_flow_capacity)

# each potential road can be built no more than once in the time horizon
def one_potential_road(k, l, model):
   return (None, sum([model.gamma[k ,l, t] for t in model.Times]), 1.0)

model.EnforceOnePotentialRoad = Constraint(model.PotentialRoads, rule=one_potential_road)

# existing roads flow capacity
def existing_roads_capacity(k, l, t, model):
	return (None, model.f[k, l, t], model.Umax)

model.EnforceExistingRoadCapacities = Constraint(model.ExistingRoads, model.Times, rule=existing_roads_capacity)

# additional road bound capacity
def additional_roads_capacity(k, l, t, model):
	return ( None, model.f[k, l, t] - sum([model.z[e, t] for e in model.ExitNodes]), 0.0 )

model.EnforceAdditionalRoadCapacities = Constraint(model.AllRoads, model.Times, rule=additional_roads_capacity)

# each cell can be harvested no more than once in the time horizon
def one_harvest(h, model):
   return (None, sum([model.delta[h,t] for t in model.Times]), 1.0)

model.EnforceOneHarvest = Constraint(model.HarvestCells, rule=one_harvest)

#
# Stage-specific profit computations
#

def stage_profit_rule(t, model):
    # ans1 is T1 (i.e. wood sale revenue)
    ans1 = sum([model.R[e, t] * model.z[e, t] for e in model.ExitNodes])
    
    # ans2 is T2 (i.e. wood harvest cost)
    ans2 = sum([model.P[h, t] * model.A[h] * model.delta[h, t] for h in model.HarvestCells])
        
    # ans3 is T3 (i.e. production costs at origin nodes)
    ans3 = sum([model.a[h, t] * model.A[h] * model.delta[h,t] * model.Q[o, t] for o in model.OriginNodes for h in model.HCellsForOrigin[o]])
           
    # ans4 is T4 (i.e. potential road construction cost)
    ans4 = sum([model.C[i, j, t] * model.gamma[i, j, t] for (i,j) in model.PotentialRoads])
    
    # ans5 is T5 (i.e. wood transport cost)
    ans5 = sum([model.D[i, j, t] * model.f[i, j, t] for (i,j) in model.AllRoads])
       
# *****
# *****
#    return (model.AnoProfit[t] - (0.9)^(t-1)*(ans1 - ans2 - ans3 - ans4 - ans5)) == 0.0
# *****
# *****
    return (model.AnoProfit[t] - (ans1 - ans2 - ans3 - ans4 - ans5)) == 0.0

model.ComputeStageProfit = Constraint(model.Times, rule=stage_profit_rule)

#
# Objective
#

def total_profit_rule(model):
   return (summation(model.AnoProfit))

model.Production_Profit_Objective = Objective(rule=total_profit_rule, sense=maximize)
