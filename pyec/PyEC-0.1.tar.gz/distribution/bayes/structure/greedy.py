from numpy import *

from basic import StructureSearch

class GreedyStructureSearch(StructureSearch):
   def __init__(self, branchFactor, scorer):
      self.branchFactor = branchFactor
      self.scorer = scorer

   def __call__(self, network, data):
      self.network = network
   
      # clear the variables
      for variable in network.variables:
         variable.parents = []
         variable.update(data)
      
      self.network.dirty = True
      self.network.computeEdgeStatistics()
      
      changes = 1
      score = 0
      while changes > 0:
         #print "changes: ", changes
         changes = 0
      
         # try to remove an edge
         #print "check remove"
         for variable in network.variables:
            shift = 0
            for idx in xrange(len(variable.parents)):
               i = idx - shift
               try:
                  undo = self.removeEdge(i, variable, data)
                  score2 = self.attempt(lambda: self.scorer(network, data), undo)
                  if score2 < score:
                     undo()
                  else:
                     #print "removed edge: ", score, score2
                     score = score2
                     shift += 1
                     changes += 1
               except:   
                  pass
                  
         
         # try to reverse an edge
         #print "check reverse"
         for variable in network.variables:
            shift = 0
            for idx in xrange(len(variable.parents)):
               i = idx - shift
               toReverse = variable.parents[i]
               if len(toReverse.parents) >= self.branchFactor:
                  continue
               if not self.canReverse(toReverse, variable):
                  continue
               
               try:
                  undo = self.reverseEdge(i, variable, data)
                  score2 = self.attempt(lambda: self.scorer(network, data), undo)
                  if score2 <= score:
                     undo()
                  else:
                     #print "reversed edge: ", score, score2
                     score = score2
                     shift += 1
                     changes += 1
               except:
                  pass  
               
         
         # try to add an edge
         #print "check add"
         for variable in network.variables:
            for variable2 in network.variables:
               if self.admissibleEdge(variable, variable2):
                  
                  if len(variable.parents) >= self.branchFactor:
                     continue
               
                  try:
                     undo = self.addEdge(variable, variable2, data)
                     score2 = self.attempt(lambda: self.scorer(network, data), undo)
                     if score2 <= score:
                        undo()
                     else:
                        #print "added edge: ", score, score2
                        score = score2
                        changes += 1
                  except:
                     pass
      return score
         
