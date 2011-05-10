class CyclicException(Exception):
   pass

class DuplicateEdgeException(Exception):
   pass
   
class IrreversibleEdgeException(Exception):
   pass   

class StructureSearch(object):
   def __init__(self, scorer, autocommit=False):
      self.scorer = scorer
      self.autocommit = autocommit
      self.network = None
      
   def canReverse(self, newChild, newParent):
      """
         check to ensure reverse link is not already present
         (In a DAG, it should not be)
      """
      return not (newParent in newChild.parents)
   
   def admissibleEdge(self, var1, var2):
      """Is edge admissible in a DAG?"""
      return var2 not in var1.parents \
             and var1 not in var2.parents \
             and var1 != var2
   
   def merge(self, net, other, data, allowCyclic=False):
      """add the edges from other to self, preventing cycles if asked"""
      self.network = net
      net.computeEdgeStatistics()
      other.computeEdgeStatistics()
      indexMap = dict([(v.index, v) for v in net.variables])
      undoList = []
      
      def undo(update=True):
         for undo2 in reversed(undoList):
            undo2(False)
         net.dirty = True
         net.computeEdgeStatistics()
         for variable in net.variables:
            variable.update(data)
            variable.children = None
         
      for frm, to in other.edges:
         try:
            frm2 = indexMap[frm.index]
            to2 = indexMap[to.index]
            undo2 = self.addEdge(to2, frm2, data, allowCyclic)
            frm2.children = None
            undoList.append(undo2)
         except Exception, msg:
            pass
      
      return undo
      
   
   def removeEdge(self, i, variable, data=None):
      toRemove = variable.parents[i]
      variable.parents = variable.parents[:i] + variable.parents[i+1:]
      toRemove.children = None
      self.network.dirty = True
            
      def undo(update=True):
         variable.parents = variable.parents[:i] + [toRemove] + variable.parents[i:]
         toRemove.children = None
         self.network.dirty = True
         self.network.computeEdgeStatistics()
         if update:
            variable.update(data)
            
      try:
         variable.update(data)
      except:
         undo()
         raise
      
      return undo      
      
      
   def addEdge(self, child, parent, data = None, allowCyclic = False):
      if parent in child.parents:
         raise DuplicateEdgeException, "Edge already exists"
      child.parents.append(parent)
      parent.children = None
      self.network.dirty = True
      
      def undo(update=True):
         parent.children = None
         child.parents = child.parents[:-1]
         self.network.dirty = True
         self.network.computeEdgeStatistics()
         if update:
            child.update(data)
      
      if (not allowCyclic) and not self.network.isAcyclic():
         undo()
         raise CyclicException, "Adding an edge makes network cyclic"
                  
      try:
         child.update(data)
      except:
         undo()
         raise            
      return undo 
      
   def reverseEdge(self, i, variable, data=None, allowCyclic = False):
      """toReverse is new child, variable is new parent"""
      toReverse = variable.parents[i]
      variable.parents = variable.parents[:i] + variable.parents[i+1:]
      toReverse.parents.append(variable)
      variable.children = None
      toReverse.children = None
      self.network.dirty = True
      
      def undo(update=True):
         variable.parents = variable.parents[:i] + [toReverse] + variable.parents[i:]
         toReverse.parents = toReverse.parents[:-1]
         self.network.dirty = True
         self.network.computeEdgeStatistics()
         variable.children = None
         toReverse.children = None
         if update:
            variable.update(data)
            toReverse.update(data)
            
      if (not allowCyclic) and not self.network.isAcyclic():
         undo()
         raise CyclicException, "Reversing an edge makes nework cyclic"
      
      try:
         variable.update(data)
         toReverse.update(data)
      except:
         undo()
         raise
      return undo
      
   def attempt(self, fn, exc):
      try:
         fn()
      except:
         exc()
         raise