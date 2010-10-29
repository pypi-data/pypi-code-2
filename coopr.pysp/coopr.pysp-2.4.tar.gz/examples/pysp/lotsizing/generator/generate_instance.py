#! /usr/bin/env python

import sys
import random

class TreeNode(object):

   def __init__(self, *args, **kwds):

      self.name = None # naming convention is "stage_nodenumwithinstage"
      self.stage_name = None # naming convention is "stage_x"
      self.stage = None # the number of the stage
      self.number_in_stage = None # the ith node in the stage
   
      # for each tree node, store the various parameters.
      self.initial_inventory = None # only at root node
      self.setup_cost = None
      self.holding_cost = None
      self.shortage_cost = None
      self.demand = None

tree_nodes = []

if len(sys.argv) != 2:
   print "***Incorrect invocation - use: generate_instance num-stages"
   sys.exit(0)

num_stages = eval(sys.argv[1])

branching_factor = 3 # hard-coded for no real good reason.

# parameters defining the range various sampled values.
initial_inventory_lower_bound = 0
initial_inventory_upper_bound = 100
setup_cost_lower_bound = 100
setup_cost_upper_bound = 500
holding_cost_lower_bound = 1
holding_cost_upper_bound = 10
shortage_cost_lower_bound = 10
shortage_cost_upper_bound = 20
demand_lower_bound = 25
demand_upper_bound = 100

random.seed()

for t in range(1, num_stages+1):

   nodes_this_stage = pow(branching_factor, t-1)

   for i in range(1, nodes_this_stage+1):

      new_tree_node = TreeNode()
      new_tree_node.name = "Node_"+str(t)+"_"+str(i)
      new_tree_node.stage_name = "Stage_"+str(t)
      new_tree_node.stage = t
      new_tree_node.number_in_stage = i

      if t == 1:
         new_tree_node.initial_inventory = random.uniform(initial_inventory_lower_bound, initial_inventory_upper_bound)

      new_tree_node.setup_cost = random.uniform(setup_cost_lower_bound, setup_cost_upper_bound)
      new_tree_node.holding_cost = random.uniform(holding_cost_lower_bound, holding_cost_upper_bound)
      new_tree_node.shortage_cost = random.uniform(shortage_cost_lower_bound, shortage_cost_upper_bound)
      new_tree_node.demand = random.uniform(demand_lower_bound, demand_upper_bound)

      tree_nodes.append(new_tree_node)

# write the scenario structure file
scenario_structure_file = open("ScenarioStructure.dat", "w")

print >>scenario_structure_file, "set Stages := "
for i in range(1, num_stages+1):
   print >>scenario_structure_file, "Stage_"+str(i)
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "set Nodes := "
for tree_node in tree_nodes:
   print >>scenario_structure_file, tree_node.name
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "param NodeStage := "
for tree_node in tree_nodes:
   print >>scenario_structure_file, tree_node.name, "   ", tree_node.stage_name
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

for tree_node in tree_nodes:
   if tree_node.stage != num_stages:
      print >>scenario_structure_file, "set Children["+tree_node.name+"] :="
      for j in range(1, branching_factor+1):
         print >>scenario_structure_file, "Node_"+str(tree_node.stage+1)+"_"+str(branching_factor * (tree_node.number_in_stage-1) + j)
      print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "param ConditionalProbability := "
for tree_node in tree_nodes:
   if tree_node.stage == 1:
      print >>scenario_structure_file, tree_node.name, "   ", "1.0"
   else:
      print >>scenario_structure_file, tree_node.name, "   ", str(1.0/branching_factor)
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "set Scenarios :="
for i in range(1, pow(branching_factor, num_stages-1)+1):
   print >>scenario_structure_file, "Scenario_"+str(i)
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "param ScenarioLeafNode := "
num_scenarios = 0
for tree_node in tree_nodes:
   if tree_node.stage == num_stages:
      num_scenarios = num_scenarios + 1
      print >>scenario_structure_file, "Scenario_"+str(num_scenarios)+"    "+tree_node.name
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "param StageCostVariable :="
for t in range(1, num_stages+1):
   print >>scenario_structure_file, "Stage_"+str(t)+"   "+"StageCost["+str(t)+"]"
print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

for t in range(1, num_stages+1):
   print >>scenario_structure_file, "set StageVariables[Stage_"+str(t)+"] := "
   print >>scenario_structure_file, "Produce["+str(t)+"]"
   print >>scenario_structure_file, "AmountProduced["+str(t)+"]"
   print >>scenario_structure_file, "Inventory["+str(t)+"]"
   print >>scenario_structure_file, "Backlog["+str(t)+"]"
   print >>scenario_structure_file, ";"
print >>scenario_structure_file, ""

print >>scenario_structure_file, "param ScenarioBasedData := False ;"
print >>scenario_structure_file, ""

scenario_structure_file.close()

# write the per-node .dat files
for tree_node in tree_nodes:
   tree_node_file = open(tree_node.name+".dat", "w")

   if tree_node.stage == 1:
      print >>tree_node_file, "param NumStages := "+str(num_stages)+" ;"
      print >>tree_node_file, ""
      print >>tree_node_file, "param InitialInventory := "+str(tree_node.initial_inventory)+" ;"
      print >>tree_node_file, ""

   print >>tree_node_file, "param SetupCost :="
   print >>tree_node_file, tree_node.stage, "  ", tree_node.setup_cost
   print >>tree_node_file, ";"
   print >>tree_node_file, ""

   print >>tree_node_file, "param HoldingCost :="
   print >>tree_node_file, tree_node.stage, "  ", tree_node.holding_cost
   print >>tree_node_file, ";"
   print >>tree_node_file, ""

   print >>tree_node_file, "param ShortageCost :="
   print >>tree_node_file, tree_node.stage, "  ", tree_node.shortage_cost
   print >>tree_node_file, ";"
   print >>tree_node_file, ""

   print >>tree_node_file, "param Demand :="
   print >>tree_node_file, tree_node.stage, "  ", tree_node.demand
   print >>tree_node_file, ";"
   print >>tree_node_file, ""

   tree_node_file.close()
