from coopr.pyomo import *

model = Model()

model.x = Var()

def objective_rule ( M ):
   return model.x * M.x    # should fail "gracefully"

model.objective = Objective(rule=objective_rule, sense=minimize)
