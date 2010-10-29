# dlw - base forest model - begin April 2009
# mnr - base forest model - revised May 1, 2009 - changed the notation of parameters to match those in paper.

from coopr.pyomo import *
import math

#
# Model
#
model = Model()
model.name = "Forest Management Base Model"

#
# Implementation Sets (not in paper, used to make it happen)
#
# general nodes (not in paper)
model.Nodes = Set()
# note from dlw: we are naming the arcs; arcsin and arcsout give endpoints
#( this is a little harder to give as data but easier for writing constraints)

# following the notation in the paper (note: nodes \equiv origins)

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

# harvest lots \mathcal{H}
model.HarvestCells = Set()

# harvest lots for origin o \mathcal{H}_o
model.HCellsForOrigin = Set(model.OriginNodes, within=model.HarvestCells)

# the origin for each harvest lot. a derived quantity.
def origin_for_hcell_rule(h, model):
   # not particularly efficient, but can't be unless you
   # somehow over-write the data initializer for the
   # HCellsForOrigin parameter.
   for o in model.OriginNodes:
      if h in model.HCellsForOrigin[o]:
         return o
   return None

model.OriginForHCell = Param(model.HarvestCells, within=model.OriginNodes, rule=origin_for_hcell_rule)

# declaring rather than deriving allroads for now...
model.AllRoads = Set()

# note from dlw: we are naming the arcs; arcsin and arcsout give endpoints
# existing roads
model.ExistingRoads = Set(within=model.AllRoads)

# potential roads
model.PotentialRoads = Set(within=model.AllRoads)

# all roads
#model.AllRoads = model.ExistingRoads + model.PotentialRoads

#
# more implementation sets
#
model.ArcsIn = Set(model.Nodes, within=model.AllRoads)
model.ArcsOut = Set(model.Nodes, within=model.AllRoads)

# the set of all potential roads that can access a particular harvest lot.
# a derived quantity.
def potential_roads_for_cell_rule(h, model):
   # have to filter out the set of potential roads from all roads -
   # arcs-in and arcs-out specify all roads.
   result = set()
   # NOTE: the parens are required to access the parameter value,
   #       as for some reason use of the parameter itself to index
   #       into an indexed set (ArcsIn) isn't working correctly.
   o = model.OriginForHCell[h]()
   for a in model.ArcsIn[o]:
      if a in model.PotentialRoads:
         result.add(a)
   return result

model.PotentialRoadsForCell = Set(model.HarvestCells, within=model.PotentialRoads, rule=potential_roads_for_cell_rule)

# back to sets described in the paper
#
# Deterministic Parameters
#

# productivity of cell h if it is harvested in period t
model.a = Param(model.HarvestCells, model.Times)

# Area of cell h to be harvested
model.A = Param(model.HarvestCells)

# flow capacity on arc (k,l) at time t
model.U = Param(model.AllRoads, model.Times)

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

# Supply of wood at exit e in period t
model.z = Var(model.ExitNodes, model.Times, domain=NonNegativeReals)

# Declared when changing the program for stochastics
model.AnoProfit = Var(model.Times)

#
# Constraints
#

# flow balance at origin nodes
# ans1 is the first term sum, ans2 the second, etc.
# we are using a for (k,0) and (0,k).
# constraint '1aflow' in Fernando's AMPL model.
def origin_flow_bal(o, t, model):
   ans1 = sum([model.a[h, t] * model.A[h] * model.delta[h, t] for h in model.HCellsForOrigin[o]])
   ans2 = sum([model.f[a, t] for a in model.ArcsIn[o]])
   ans3 = sum([model.f[a, t] for a in model.ArcsOut[o]])
   return (ans1 + ans2 - ans3) == 0.0

model.EnforceOriginFlowBalance = Constraint(model.OriginNodes, model.Times, rule=origin_flow_bal)

# flow balance at intersection nodes.
# we are using a for (k,j) and (j,k).
# constraint '1bflow' in Fernando's AMPL model.
def intersection_flow_bal(j, t, model):
   return (sum([model.f[a, t] for a in model.ArcsIn[j]]) - sum([model.f[a, t] for a in model.ArcsOut[j]])) == 0.0

model.EnforceIntersectionFlowBalance = Constraint(model.IntersectionNodes, model.Times, rule=intersection_flow_bal)

# flow balance at destination nodes.
# constraint '1cflow' in Fernanod's AMPL model.
def destination_flow_bal(e, t, model):
   return (model.z[e, t] - sum([model.f[a, t] for a in model.ArcsIn[e]]) + sum([model.f[a, t] for a in model.ArcsOut[e]])) == 0.0

model.EnforceDestinationFlowBalance = Constraint(model.ExitNodes, model.Times, rule=destination_flow_bal)

# zero divergence condition - everything that is harvested in a time period must exit somewhere.
# constraint 1dflow in Fernando's AMPL model.
def zero_divergence_flow_bal(t, model):
   return (sum([model.a[h, t] * model.A[h] * model.delta[h, t] for h in model.HarvestCells]) - sum([model.z[e, t] for e in model.ExitNodes])) == 0.0

model.EnforceZeroDivergenceFlowBalance = Constraint(model.Times, rule=zero_divergence_flow_bal)

# enforce wood production bounds.
# constraints '2demandlb' and '2demandub' in Fernando's AMPL model.
def wood_prod_bounds(t, model):
   return (model.Zlb[t], sum([model.z[e, t] for e in model.ExitNodes]), model.Zub[t])

model.EnforceWoodProductionBounds = Constraint(model.Times, rule=wood_prod_bounds)

# potential roads flow capacity
# we are using a for (k,l)
# constraint '3aroadcap' in Fernando's AMPL model.
def pot_road_flow_capacity(a, t, model):
   return (None, model.f[a, t] - sum([model.U[a, t] * model.gamma[a, tau] for tau in model.Times if tau <= t]), 0.0)

model.EnforcePotentialRoadFlowCap = Constraint(model.PotentialRoads, model.Times, rule=pot_road_flow_capacity)

# each potential road can be built no more than once in the time horizon.
# we use a for (k,l).
# constraint '3boneroadb' in Fernando's AMPL model.
def one_potential_road(a, model):
   return (0.0, sum([model.gamma[a, t] for t in model.Times]), 1.0)   

model.EnforceOnePotentialRoad = Constraint(model.PotentialRoads, rule=one_potential_road)

# existing roads flow capacity.
# we are using a for (k,l).
# constraint '4xroadcap' in Fernando's model.
def existing_roads_capacity(a, t, model):
   return (0.0, model.f[a,t], model.U[a,t])

model.EnforceExistingRoadCapacities = Constraint(model.ExistingRoads, model.Times, rule=existing_roads_capacity)

# the flow for any road can't exceed the amount harvested in a period.
# we are using a for (k.l).
# constraint '4allroadcap' in Fernando's model.
def all_roads_capacity(a, t, model):
   return (0.0, (sum([model.a[h, t] * model.A[h] * model.delta[h, t] for w in model.OriginNodes for h in model.HCellsForOrigin[w]]) - model.f[a, t]), None)

model.EnforceAllRoadsFlowCapacity = Constraint(model.AllRoads, model.Times, rule=all_roads_capacity)

# each cell can be harvested no more than once in the time horizon
def one_harvest(h, model):
   return (0.0, sum([model.delta[h,t] for t in model.Times]), 1.0)

model.EnforceOneHarvest = Constraint(model.HarvestCells, rule=one_harvest)

# isolated lots shouldn't be harvested.
# constraint '8lottoroad' in Fernando's model.
# TBD: This constraint is yielding infeasibility.
#def isolated_lot_harvest_prevention(h, t, model):
#   return (0.0, sum([model.gamma[a, g] for g in model.Times if g <= t for a in model.PotentialRoadsForCell[h]]) - model.delta[h, t], None)
   
#model.EnforceIsolatedLotHarvestPrevention = Constraint(model.HarvestCells, model.Times, rule=isolated_lot_harvest_prevention)

#
# Stage-specific profit computations
#

def stage_profit_rule(t, model):
    # ans1 is T1 (i.e. wood sale revenue)
    ans1 = sum([model.R[e, t] * model.z[e, t] for e in model.ExitNodes])
    
    # ans2 is T2 (i.e. wood harvest cost)
    ans2 = sum([model.P[h, t] * model.A[h] * model.delta[h, t] for h in model.HarvestCells])
        
    # ans3 is T3 (i.e. production costs at origin nodes).
    ans3 = sum([model.a[h, t] * model.A[h] * model.delta[h,t] * model.Q[o, t] for o in model.OriginNodes for h in model.HCellsForOrigin[o]])
           
    # ans4 is T4 (i.e. potential road construction cost)
    # we are using a for (k,l)
    ans4 = sum([model.C[a, t] * model.gamma[a, t] for a in model.PotentialRoads])
    
    # ans5 is T5 (i.e. wood transport cost)
    # we are using a for (k,l)
    ans5 = sum([model.D[a, t] * model.f[a, t] for a in model.AllRoads])

    # the discounted version.
#    return (model.AnoProfit[t] - (math.pow(0.9,model.Times.ord(t)) * (ans1 - ans2 - ans3 - ans4 - ans5))) == 0.0

    # the non-discounted verson.
    return (model.AnoProfit[t] - (ans1 - ans2 - ans3 - ans4 - ans5)) == 0.0 

model.ComputeStageProfit = Constraint(model.Times, rule=stage_profit_rule)

#
# Objective
#

def total_profit_rule(model):
   return (summation(model.AnoProfit))

model.Production_Profit_Objective = Objective(rule=total_profit_rule, sense=maximize)
