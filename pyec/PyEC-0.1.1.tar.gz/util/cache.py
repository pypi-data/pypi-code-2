from time import time

class LLNode(object):
   before = None
   after = None
   value = None

class LinkedList(object):
   first = None
   last = None
   
   def append(value):
      node = LLNode()
      node.value = value
      before = self.last
      after = None
      self.last = node
      if self.first is None:
         self.first = node

   def remove(node):
      if node == self.first:
         self.first = node.after
      if node == self.last:
         self.last = node.before
      if node.before is not None:
         node.before.after = node.after
      if node.after is not None:
         node.after.before = node.before

class LRUCache(object):

   def __init__(self, size=10000):
      self.maxSize = size
      self.times = LinkedList()
      self.objects = {}
      self.timeMap = {}
    
   def __setitem__(self, key, val):
      if self.timeMap.has_key(key):
         node = self.timeMap[key]
         self.times.remove(node)
      self.objects[key] = val
      timeNode = LLNode()
      timeNode.value = key
      self.times.append(node)
      self.timeMap[key] = node
      while len(self.objects) > self.maxSize:
         lru = self.times.first
         del self.timeMap[lru.value]
         del self.objects[lru.value]
         self.times.remove(lru)
         
   def __getitem__(self, key):
      return self.objects[key]

   def __len__(self):
      return len(self.objects)
      

         