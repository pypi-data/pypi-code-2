import cPickle
from cStringIO import StringIO
from variables import VariableComparator
from sample import *
from structure import *
from variables import *
from pyec.distribution.basic import Distribution

class BayesNet(Distribution):
   def __init__(self, config):
      super(BayesNet, self).__init__(config)
      self.numVariables = config.dim
      self.variableGenerator = config.variableGenerator
      self.structureGenerator = config.structureGenerator
      self.randomizer = config.randomizer
      self.sampler = config.sampler
   
      self.variables = []
      for i in xrange(self.numVariables):
         self.variables.append(self.variableGenerator(i))
      self.decay = 1
      self.dirty = False
      self.acyclic = True
      self.edges = []
      self.edgeRatio = 0.0
      self.binary = zeros(len(self.variables)**2)
      
   def randomize(self):
      return self.randomizer(self)  
      
   def likelihood(self, data):
      prod = 0.0
      for x in data:
         prod += log(self.density(x))
      return prod
      
   def density(self, x):
      prod = 1.0
      for variable in self.variables:
         prod *= variable.density(x)
      return prod
      
   def __call__(self):
      """sample the network"""
      return self.sampler(self)

   def batch(self, num):
      return [self.__call__() for i in xrange(num)]

   def numFreeParameters(self):
      total = 0
      for variable in self.variables:
         total += variable.numFreeParameters()
      return total

   def update(self, epoch, data):
      self.variables = sorted(self.variables, key=lambda x: VariableComparator(x))
      for variable in self.variables:
         variable.update(data)
   
   def merge(self, other, data):
      return self.structureGenerator.merge(self, other, data)                  

   def hasEdge(self, frm, t):
      """has an edge from the parent with index 'from'
         to the child with index 'to'
         
         TODO: improve efficiency; current implementation N^2
         can be made constant
      """
      try:
         toNode = [variable for variable in self.variables if variable.index == t][0]
         fromNode = [parent for parent in fromNode.parents if parent.index == frm][0]
         return True
      except:
         return False

   def isAcyclic(self):
      """Is the network a DAG?"""
      if not self.dirty: return self.acyclic
      self.computeEdgeStatistics()
         
      tested = set([])
      for variable in self.variables:
         if len(set(variable.parents) - tested) > 0:
            self.acyclic = False
            return False
         tested = set(list(tested) + [variable])
      self.acyclic = True   
      return True   
         
      
      """
      for variable in self.variables:
         if variable in variable.parents:
            return False
            
      tested = set([])
      while len(tested) < len(self.variables):
        added = False
        for variable in self.variables:
            if variable in tested:
               continue
            if len(set(variable.parents) - tested) == 0:
               tested = set(list(tested) + [variable])
               added = True
               break
        if not added:
           return False
      return True
      """

   def structureSearch(self, data):
      return self.structureGenerator(self, data)
      
   def computeEdgeStatistics(self):
      if not self.dirty: return
      
      self.variables = sorted(self.variables, key=lambda x: VariableComparator(x))
      if self.edges is not None: del self.edges
      self.edges = []
      for variable in self.variables:
         for variable2 in variable.parents:
            self.edges.append((variable2, variable))
      self.edges = sorted(self.edges, key=lambda e: (e[0].index,e[1].index))
      self.edgeRatio = len(self.edges) / (1e-10 + (len(self.variables) ** 2))
      self.edgeBinary()
      self.edgeTuples = [(frm.index, to.index) for frm,to in self.edges]
      self.dirty = False
   
      
   def getChildren(self, variable):
      children = []
      for variable2 in self.variables:
         if variable in variable2.parents:
             children.append(variable2)
      return children
   
   def updateVariables(self, data):
      for variable in self.variables:
         variable.update(data)
   
   def edgeBinary(self):
      if not self.dirty: return self.binary
      if self.binary is not None: del self.binary
      ret = zeros(len(self.variables)**2)
      for frm,t in self.edges:
         idx = frm.index + len(self.variables) * t.index
         ret[idx] = 1
      self.binary = ret
      return ret
            
   def __getstate__(self):
      return {
         'v': self.variables,
         'r': self.randomizer,
         's': self.sampler,
         'sg': self.structureGenerator
      }
      
   def __setstate__(self, state):
      self.dirty = True
      self.variables = state['v']
      self.randomizer = state['r']
      self.structureGenerator = state['sg']
      self.sampler = state['s']
      indexMap = {}
      for variable in self.variables:
         indexMap[variable.index] = variable
      for variable in self.variables:
         variable.parents = []
         for i in variable.parentIndices:
            variable.parents.append(indexMap[i])
            
      self.edges = None
      self.binary = None
      self.computeEdgeStatistics()
      
   def __str__(self):
      """pickle the object"""
      self.computeEdgeStatistics()
      return cPickle.dumps(len(self.variables)) + cPickle.dumps(self.edgeTuples)
      
   @classmethod
   def parse(cls, rep, cfg):
      #inst = cPickle.load(StringIO(rep))
      
      io = StringIO(rep)
      numVars = cPickle.load(io)
      net = cls(numVars, cfg.variableGenerator, cfg.structureGenerator, cfg.randomizer, cfg.sampler)
      edges = cPickle.load(io)
      net.variables = sorted(net.variables, key=lambda x: x.index)
      for frm,to in edges:
         net.variables[to].parents.append(net.variables[frm])
      for variable in net.variables:
         variable.update(cfg.data)
      net.dirty = True
      net.computeEdgeStatistics()
      
      
      return net

      
