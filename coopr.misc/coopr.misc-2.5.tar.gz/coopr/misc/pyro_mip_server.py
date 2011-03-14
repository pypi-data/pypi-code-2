#! /usr/bin/env python
#
# pyro_mip_server: A script that sets up a Pyro server for solving MIPs in 
#           a distributed manner.
#
#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2008 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the FAST README.txt file.
#  _________________________________________________________________________

import os
import os.path
import sys
try:
   import cPickle as pickle
except ImportError:
   import pickle
import pyutilib.services
import pyutilib.pyro
import coopr.opt


class CooprMIPWorker(pyutilib.pyro.TaskWorker):

    def process(self, data):
        # construct the solver on this end, based on the input type stored in "data.opt".
        opt = coopr.opt.SolverFactory(data.opt)
        if opt is None:
            raise ValueError, "Problem constructing solver `"+data.opt+"'"
        opt.mipgap = data.mipgap
        opt.suffixes = data.suffixes

        # here is where we should set any options required by the solver, available
        # as specific attributes of the input data object.
        solver_options = data.solver_options
        del data.solver_options
        for key,value in solver_options.items():
#            print "RECEIVED SOLVER OPTION="+key+"WITH VALUE="+value
            setattr(opt.options,key,value)

        problem_filename_suffix = os.path.split(data.filename)[1]
        temp_problem_filename = pyutilib.services.TempfileManager.create_tempfile(suffix="."+problem_filename_suffix)
        OUTPUT=open(temp_problem_filename,'w')
        print >>OUTPUT, data.file,
        OUTPUT.close()

        if data.warmstart_file is not None:
           warmstart_filename_suffix = os.path.split(data.warmstart_filename)[1]
           temp_warmstart_filename = pyutilib.services.TempfileManager.create_tempfile(suffix="."+warmstart_filename_suffix)
           OUTPUT=open(temp_warmstart_filename,'w')
           print >>OUTPUT, data.warmstart_file
           OUTPUT.close()
           opt.warm_start_solve = True
           opt.warm_start_file_name = temp_warmstart_filename
        
        print "Applying solver="+data.opt+" to solve problem="+temp_problem_filename
        results = opt.solve(temp_problem_filename, **data.kwds)
        # attach the symbol map.
        results.symbol_map = data.symbol_map
        pyutilib.services.TempfileManager.clear_tempfiles()
        # disabling write of solutions for now - this was getting too verbose,
        # especially when running Progressive Hedging.
        print "Solve completed - number of solutions="+str(len(results.solution))
        sys.stdout.flush()
#        results.write()
#        sys.stdout.flush()
        return pickle.dumps(results)


def main():
    pyutilib.pyro.TaskWorkerServer(CooprMIPWorker, argv=sys.argv)

