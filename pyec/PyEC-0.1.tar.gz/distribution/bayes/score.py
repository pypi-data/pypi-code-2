from numpy import *
from scipy.special import gamma, gammaln
from pyec.util.cache import LRUCache      

class BayesianDirichletScorer(object):
   def __init__(self):
      self.cache = {}
      self.varCache = LRUCache()

   def matchesPrior(self, data, configuration):
      return 1.0
      
   def matches(self, data, config):
      """count number of instances of configuration in data"""
      cnt = 0L
      for x in data:
         if config <= x:
            cnt += 1
      #print "matches: ", cnt, len(data)
      return cnt
      
      
   def __call__(self, network, data):
      network.computeEdgeStatistics()
      #rep = str(network.edges)
      #if self.cache.has_key(rep):
      #   return self.cache[rep]
      total = 0.0
      total -= network.edgeRatio * len(data) * 10
      for variable in network.variables:
         varKey = str(variable.index) + str(variable.parents)
         if self.varCache.has_key(varKey):
            total += self.varCache[varKey]
            continue
         start = total
         for configuration in variable.configurations():
            prior = self.matchesPrior(data, configuration)
            total += gammaln(prior)
            total -= gammaln(prior + self.matches(data, configuration))
            #print "total", total
            for val in variable.values():
               priorVal = self.matchesPrior(data, configuration + val)
               total -= gammaln(priorVal)
               total += gammaln(priorVal + self.matches(data, configuration + val))
               #print "total", total
         self.varCache[varKey] = total - start
      #self.cache[rep] = total   
      return total / len(data)

class BayesianInformationCriterion(object):
   def __init__(self, lmbda = .5):
      self.lmbda = lmbda

   def __call__(self, network, data):
      network.computeEdgeStatistics()
      total = 0
      #total = -4 * self.lmbda * log(len(network.variables)) * len(network.edges)
      #total -= len(network.edges) * log(len(data))
      #total += 2 * network.likelihood(data)
      
      total -= log(network.numFreeParameters()) * .5 * log(len(data))
      total += network.likelihood(data)
      
      return total / len(data)
