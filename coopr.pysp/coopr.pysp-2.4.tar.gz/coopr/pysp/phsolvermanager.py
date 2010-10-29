#  _________________________________________________________________________
#
#  Coopr: A COmmon Optimization Python Repository
#  Copyright (c) 2010 Sandia Corporation.
#  This software is distributed under the BSD License.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  For more information, see the Coopr README.txt file.
#  _________________________________________________________________________


__all__ = []

import Pyro.core
import Pyro.naming

from coopr.opt.parallel.manager import *
from coopr.opt.parallel.solver import *
from coopr.pyomo import *
from pyutilib.component.core import alias

try:
   import cPickle as pickle
except ImportError:
   import pickle

# a solver manager that communicates with remote PH solver servers
# via the Pyro RMI mechanism.

class PHSolverManager(AsynchronousSolverManager):

    alias('ph')

    def __init__(self):
        """Constructor"""

        AsynchronousSolverManager.__init__(self)

        # fire up Pyro.
        Pyro.core.initClient(banner=0)        

        # locate the name server and cache it.
        self._locator = Pyro.naming.NameServerLocator()
        self._ns = None
        try:
           self._ns = self._locator.getNS()
        except Pyro.errors.NamingError:
           raise RuntimeError, "PHSolverManager failed to locate Pyro name server"

        # the PH solver server object proxies are cached for speed.
        # map is from scenario name to proxy object.
        self._solver_proxy = {}

    # 
    # a utility to identify (and create if necessary) the 
    # appropriate proxy object for a given scenario.
    #

    def _identify_proxy(self, scenario_name):

       proxy = None
       if scenario_name in self._solver_proxy.keys():
          proxy = self._solver_proxy[scenario_name]
       else:
          uri = None
          try:
             uri = self._ns.resolve(scenario_name)
          except Pyro.errors.NamingError:
             raise RuntimeError, "***ERROR: Failed to locate PH solver server capable of processing scenario="+scenario_name
             sys.exit(0)

          proxy = Pyro.core.getProxyForURI(uri)
          self._solver_proxy[scenario_name] = proxy
       return proxy

    def clear(self):
        """
        Clear manager state
        """
        AsynchronousSolverManager.clear(self)
        self._ah_list = []
        self._opt = None

    def _perform_queue(self, ah, *args, **kwds):
        """
        Perform the queue operation.  This method returns the ActionHandle,
        and the ActionHandle status indicates whether the queue was successful.
        """
        
        # extract the instance and the scenario name.
        if len(args) != 1:
           raise RuntimeError, "Only one argument to _perform_queue method of class PHSolverManager expected - "+str(len(args))+" were supplied"
        scenario_instance = args[0]
        if isinstance(scenario_instance, Model) is False:
           raise RuntimeError, "Argument supplied to _perform_queue method of class PHSolverManager must be a Model instance - type supplied="+str(type(scenario_instance))
        scenario_name = scenario_instance.name

        # process any keywordds - we generally don't expect any.
        if 'opt' in kwds:
            self._opt = kwds['opt']
            del kwds['opt']
        if self._opt is None:
            raise ActionManagerError, "Undefined solver"

        # TBD - we don't actually transfer any solver options
        #       at the moment, but we will soon!

        proxy = self._identify_proxy(scenario_name)
        encoded_result = proxy.solve(scenario_name)
        self.results[ah.id] = pickle.loads(encoded_result)
        ah.status = ActionStatus.done
        self._ah_list.append(ah)
        return ah

    def _perform_wait_any(self):
        """
        Perform the wait_any operation.  This method returns an
        ActionHandle with the results of waiting.  If None is returned
        then the ActionManager assumes that it can call this method again.
        Note that an ActionHandle can be returned with a dummy value,
        to indicate an error.
        """
        if len(self._ah_list) > 0:
            return self._ah_list.pop()
        return ActionHandle(error=True, explanation="No queued evaluations available in the PH solver manager, which only executes solvers synchronously")

    def enable_ph_objective(self, scenario_instance):

       proxy = self._identify_proxy(scenario_instance.name)
       proxy.enable_ph_objective()

    def transmit_weights_and_averages(self, scenario_instance, new_weights, new_averages):

       proxy = self._identify_proxy(scenario_instance.name)
       proxy.update_weights_and_averages(scenario_instance.name, new_weights, new_averages)

    def transmit_rhos(self, scenario_instance, new_rhos):

       proxy = self._identify_proxy(scenario_instance.name)
       proxy.update_rhos(scenario_instance.name, new_rhos)

    def transmit_tree_node_statistics(self, scenario_instance, tree_node_minimums, tree_node_maximums):
       
       proxy = self._identify_proxy(scenario_instance.name)
       proxy.update_tree_node_statistics(scenario_instance.name, tree_node_minimums, tree_node_maximums)    

