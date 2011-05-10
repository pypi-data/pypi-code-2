import traceback, sys

from numpy import *

from basic import StructureSearch, CyclicException
from pyec.distribution.bayes.net import BayesNet
from pyec.distribution.bayes.variables import VariableComparator


class ProbDecayInvEdgeRatio(object):
   def __init__(self, alpha=0.75):
      self.alpha = alpha

   def __call__(self, network):
      decay = network.decay
      edgeRatio = 1. - network.edgeRatio
      adjEdgeRatio = edgeRatio + 1./(len(network.variables)**2)
      num = 1. - (adjEdgeRatio ** self.alpha)
      denom = 1. - (edgeRatio ** self.alpha)
      if num <= 0.0 or denom <= 0.0:
         return 0.0
      return (.25 + .75*(1. - num / denom)) ** decay 

class ProbDecayEdgeRatio(object):
   def __init__(self, alpha=0.5):
      self.alpha = alpha
      
   def __call__(self, network):
      decay = network.decay
      adjEdgeRatio = 1./(len(network.variables)**2) + network.edgeRatio
      num = 1. - (adjEdgeRatio ** self.alpha)
      denom = 1. - (network.edgeRatio ** self.alpha)
      if denom == 0.0:
         return 0.0
      return (num / denom) ** decay 

class StructureProposal(StructureSearch):
   def __init__(
      self, 
      config,
      prem=ProbDecayInvEdgeRatio(), 
      padd=ProbDecayEdgeRatio(), 
      prev=ProbDecayEdgeRatio()
   ):
      """
         params:
         
         prem - function to prob of removing node given network
         padd - function to prob of adding node given network
         prev - function to prob of reversing an edge given network
      """
      self.prem = prem
      self.padd = padd
      self.prev = prev
      self.config = config
      self.network = None
      self.data = None

   def __getstate__(self):
      return {'prem':self.prem,'padd':self.padd,'prev':self.prev}
      
   def __setstate__(self, state):
      self.data = None
      self.network = None
      self.config = None
      self.prem = state['prem']
      self.prev = state['prev']
      self.padd = state['padd']
   

   
   def maybeChange(self, p, changer, existing=True):
      changed = False
      try:
         if random.random_sample() < p(self.network):
            # pick a random edge
            if existing:
               if len(self.network.edges) == 0:
                  return False
               index = random.randint(0, len(self.network.edges))
               parent, child = self.network.edges[index]
               changer(child.parents.index(parent), child, self.data)
            else:
               indexFrom = indexTo = 0
               exists = False
               while indexFrom == indexTo or exists:
                  indexFrom = random.randint(0, len(self.network.variables))
                  indexTo = random.randint(0, len(self.network.variables))
                  exists = self.network.variables[indexFrom] in self.network.variables[indexTo].parents
               #print "adding ", indexFrom, indexTo
               changer(self.network.variables[indexTo], self.network.variables[indexFrom], self.data)
            changed = True
            self.network.computeEdgeStatistics()
      except CyclicException, msg:
         pass
      except Exception, msg:
         print Exception, msg
         traceback.print_exc(file=sys.stdout)
      return changed

   def __call__(self, network=None, data=None, **kwargs):
      if network:
         self.network = network
      elif kwargs.has_key('prior'):
         self.network = kwargs['prior']
      else:
         self.network = BayesNet(
            self.config.numVariables,
            self.config.variableGenerator, 
            self, 
            self.config.randomizer
         )
         self.network.updateVariables(self.config.data)
      if data:
         self.data = data
      else:
         self.data = self.config.data
      self.network.computeEdgeStatistics()
      
      total = 0
      changes = 1
      while total == 0: # changes > 0:
         changes = 0
         
         #print "add: ", self.padd(self.network), "rem: ", self.prem(self.network)
         
         # remove an edge
         if self.maybeChange(self.prem, self.removeEdge):
            changes += 1 
         
         # reverse an edge
         if self.maybeChange(self.prev, self.reverseEdge):
            changes += 1
         
         # add an edge
         if self.maybeChange(self.padd, self.addEdge, False):
            changes += 1
         
         total += changes
      
      #print self.network.edges
      self.network.variables = sorted(self.network.variables, key=lambda x: VariableComparator(x))
      
      return self.network
            
   def __getstate__(self):
      self.data = None
      self.network = None
      return self.__dict__
      
   def __setstate__(self,state):
      state['network'] = None
      state['data'] = None
      self.__dict__.update(state)
      
                     
   def adjust(self, acceptanceRatio):
      """Called by simulated annealing to update generation statistics"""

   def densityRatio(self, x, y, i):
      """Called by simulated annealing to adjust for assymetric densities
         The density governing this proposal should be symmetric.
         Still need to check this claim
      """
      return 1.0
         
         
