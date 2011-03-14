import sys
import os
import time
import traceback

from coopr.pysp.scenariotree import *
from coopr.pysp.convergence import *
from coopr.pysp.ph import *
from coopr.pysp.ef import *

# plug-in imports go here!!!
from coopr.pysp import wwphextension

# for profiling
try:
    import cProfile as profile
except ImportError:
    import profile
import pstats

def run_ph():

   start_time = time.time()

   #
   # create and populate the core model
   #

   modelimport = pyutilib.import_file("ReferenceModel.py")
   filter_excepthook=False
   if "model" not in dir(modelimport):
      print ""
      print "Exiting test driver: No 'model' object created in module "+"ReferenceModel.py"
      sys.exit(0)
   if modelimport.model is None:
      print ""
      print "Exiting test driver: 'model' object equals 'None' in module "+"ReferenceModel.py"
      sys.exit(0)
 
   instance = modelimport.model.create("ReferenceModel.dat")

   #
   # create and populate the scenario tree model
   #

   treeimport = pyutilib.import_file("ScenarioStructure.py")
   # add checks for various expected objects here, e.g., "Nodes" and the like.

   tree_data = treeimport.model.create("ScenarioStructure.dat")

   #
   # construct the scenario tree
   #
   scenario_tree = ScenarioTree(model=instance,
                                nodes=tree_data.Nodes,
                                nodechildren=tree_data.Children,
                                nodestages=tree_data.NodeStage,
                                nodeprobabilities=tree_data.ConditionalProbability,
                                stages=tree_data.Stages,
                                stagevariables=tree_data.StageVariables,
                                stagecostvariables=tree_data.StageCostVariable,
                                scenarios=tree_data.Scenarios,
                                scenarioleafs=tree_data.ScenarioLeafNode,
                                scenariobaseddata=tree_data.ScenarioBasedData)

   # print the input tree for validation/information purposes.
   #
   scenario_tree.pprint()

   #
   # validate the tree prior to doing anything serious
   #
   print ""
   if scenario_tree.validate() is False:
      print "***Scenario tree is invalid****"
      sys.exit(1)
   else:
      print "Scenario tree is valid!"
   print ""

   #
   # construct the convergence "computer" class.
   #
   converger = TermDiffConvergence(convergence_threshold=0.01)
   
   #
   # construct and initialize PH
   #
   ph = ProgressiveHedging(max_iterations=100, rho=0.01, solver="cplex", keep_solver_files=False, output_solver_results=False, verbose=True, output_times=True, rho_setter="rhosetter.cfg")
   ph.initialize(scenario_data_directory_name=".", model=modelimport.model, model_instance=instance, scenario_tree=scenario_tree, converger=converger)

   #
   # kick off the solve
   #
   ph.solve()

   print ""
   print "DONE..."

   end_time = time.time()

   print ""
   print "Total execution time=%8.2f seconds" %(end_time - start_time)
   print ""
   ph.print_time_stats()


   # write the extensive form, accounting for any fixed variables.
   print ""
   print "Writing EF for remainder problem"
   print ""
   write_ef(ph._scenario_tree,ph._instances,"efout.lp")

# execute it!
if 1:
   try:
      run_ph()
   except RuntimeError:
      print "***Runtime error encountered - traceback:"
      traceback.print_exc()      
else:
   profile.run('run_ph()','profile.stats')
   p=pstats.Stats('profile.stats')
   p.sort_stats('time')
#   p.sort_stats('cumulative')
   p.print_stats()
#   p.print_callers()

