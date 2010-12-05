#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


from gurobipy import *

def gurobi_run(model_file, warmstart_file, soln_file, mipgap, options):

    # Load the lp model
    model = read(model_file)

    if warmstart_file is not None:
       model.read(warmstart_file)

    # set the mipgap if specified.
    if mipgap is not None:
       model.setParam("MIPGap", mipgap)
 
    # set all other solver parameters, if specified.
    # GUROBI doesn't throw an exception if an unknown
    # key is specified, so you have to stare at the
    # output to see if it was accepted.
    for key, value in options.iteritems():
       model.setParam(key, value)
    
    # optimize the model
    model.optimize()

    ###
    # write the solution file
    ###
    solnfile = open(soln_file, "w+")

    # write the information required by results.problem
    print >>solnfile, "section:problem"
    name = model.getAttr(GRB.Attr.ModelName)
    print >>solnfile, "name:",name

    sense = model.getAttr(GRB.Attr.ModelSense)

    # TODO: find out about bounds and fix this with error checking
    # this line fails for some reason so set the value to unknown
    #bound = model.getAttr(GRB.Attr.ObjBound)
    bound = 'unknown'
    if (sense > 0):
        print >>solnfile, "sense:maximize"
        print >>solnfile, "upper_bound:",bound
    else:
        print >>solnfile, "sense:minimize"
        print >>solnfile, "lower_bound:",bound

    # TODO: Get the number of objective functions from GUROBI
    n_objs = 1
    print >>solnfile, "number_of_objectives:", n_objs

    cons = model.getConstrs()
    print >>solnfile, "number_of_constraints:",len(cons)

    vars = model.getVars()
    print >>solnfile, "number_of_variables:",len(vars)

    n_binvars = model.getAttr(GRB.Attr.NumBinVars)
    print >>solnfile, "number_of_binary_variables:", n_binvars

    n_intvars = model.getAttr(GRB.Attr.NumIntVars)
    print >>solnfile, "number_of_integer_variables:", n_intvars

    print >>solnfile, "number_of_continuous_variables:", len(vars)-n_intvars

    print >>solnfile, "number_of_nonzeros:",model.getAttr(GRB.Attr.NumNZs)

    # write out the information required by results.solver
    print >>solnfile, "section:solver"
    print >>solnfile, "solver_ID:", "GUROBI"
    
    solver_status = model.getAttr(GRB.Attr.Status)
    if (solver_status == GRB.LOADED):
        status = 'aborted'
        return_code = 'GRB.LOADED'
        message = 'Model is loaded, but no solution information is availale.'
        term_cond = 'unsure'
    elif (solver_status == GRB.OPTIMAL):
        status = 'ok'
        return_code = 'GRB.OPTIMAL'
        message = 'Model was solved to optimality (subject to tolerances), and an optimal solution is available.'
        term_cond = 'globallyOptimal'
    elif (solver_status == GRB.INFEASIBLE):
        status = 'warning'
        return_code = 'GRB.INFEASIBLE'
        message = 'Model was proven to be infeasible.'
        term_cond = 'infeasible'
    elif (solver_status == GRB.INF_OR_UNBD):
        status = 'warning'
        return_code = 'GRB.INF_OR_UNBD'
        message = 'Problem proven to be infeasible or unbounded.'
        term_cond = 'infeasible' # Coopr doesn't have an analog to "infeasible or unbounded", which is a weird concept anyway.
    elif (solver_status == GRB.UNBOUNDED):
        status = 'warning'
        return_code = 'GRB.UNBOUNDED'
        message = 'Model was proven to be unbounded.'
        term_cond = 'unbounded'
    elif (solver_status == GRB.CUTOFF):
        status = 'aborted'
        return_code = 'GRB.CUTOFF'
        message = 'Optimal objective for model was proven to be worse than the value specified in the Cutoff  parameter. No solution information is available.'
        term_cond = 'minFunctionValue'
    elif (solver_status == GRB.ITERATION_LIMIT):
        status = 'aborted'
        return_code = 'GRB.ITERATION_LIMIT'
        message = 'Optimization terminated because the total number of simplex iterations performed exceeded the value specified in the IterationLimit parameter.'
        term_cond = 'maxIterations'
    elif (solver_status == GRB.NODE_LIMIT):
        status = 'aborted'
        return_code = 'GRB.NODE_LIMIT'
        message = 'Optimization terminated because the total number of branch-and-cut nodes explored exceeded the value specified in the NodeLimit parameter.'
        term_cond = 'stoppedByLimit'
    elif (solver_status == GRB.TIME_LIMIT):
        status = 'aborted'
        return_code = 'GRB.TIME_LIMIT'
        message = 'Optimization terminated because the time expended exceeded the value specified in the TimeLimit parameter.'
        term_cond = 'stoppedByLimit'
    elif (solver_status == GRB.SOLUTION_LIMIT):
        status = 'aborted'
        return_code = 'GRB.SOLUTION_LIMIT'
        message = 'Optimization terminated because the number of solutions found reached the value specified in the SolutionLimit parameter.'
        term_cond = 'stoppedByLimit'
    elif (solver_status == GRB.INTERRUPTED):
        status = 'aborted'
        return_code = 'GRB.INTERRUPTED'
        message = 'Optimization was terminated by the user.'
        term_cond = 'error'
    elif (solver_status == GRB.NUMERIC):
        status = 'error'
        return_code ='GRB.NUMERIC'
        message = 'Optimization was terminated due to unrecoverable numerical difficulties.'
        term_cond = 'error'
    else:
        status = 'error'
        return_code = 'UNKNOWN'
        message = 'Unknown return code from GUROBI model.getAttr(GRB.Attr.Status) call'
        term_cond = 'unsure'
    
    print >>solnfile, 'status:', status
    print >>solnfile, 'return_code:', return_code
    print >>solnfile, 'message:',message
    print >>solnfile, 'user_time:', model.getAttr(GRB.Attr.Runtime)
    print >>solnfile, 'system_time:', str(0.0)
    print >>solnfile, 'termination_condition:', term_cond
    print >>solnfile, 'termination_message:', message

    is_discrete = False
    if (model.getAttr(GRB.Attr.IsMIP)):
       is_discrete = True

    #TODO: Can we query GUROBI to find out if an incumbent exists
    if (term_cond == 'globallyOptimal'):
        print >>solnfile, 'section:solution'
        print >>solnfile, 'status:globallyOptimal'
        print >>solnfile, 'message:',message
        obj_value = model.getAttr(GRB.Attr.ObjVal)
        print >>solnfile, 'objective:',obj_value

        for var in vars:
            print >>solnfile, 'variable:',var.getAttr(GRB.Attr.VarName), ":",var.getAttr(GRB.Attr.X)

        if is_discrete is False:
           for con in cons:
               # Pi attributes in Gurobi are the constraint duals
               print >>solnfile, "constraint:",con.getAttr(GRB.Attr.ConstrName),":",con.getAttr(GRB.Attr.Pi)

    solnfile.close()


