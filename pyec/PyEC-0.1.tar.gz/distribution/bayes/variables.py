from numpy import *
import numpy.linalg
from pyec.util.TernaryString import TernaryString

seterr(divide="ignore")

class BayesVariable(object):
   def __init__(self, index):
      self.index = index
      self.parents = []
      self.children_ = None
      
   def __call__(self, x):
      """sample the variable, conditional on x"""
      pass
      
   def project(self, x):
      prj = [x[self.index]]
      for parent in self.parents:
         prj.append(x[parent.index])
      return array(prj)
      
   def update(self, data):
      pass
      
   def isset(self, x): 
      return True   
      
   def density(self, x):
      pass
   
   def marginalDensity(self, x, network):
      pass         
                              
   def marginal(self, x, network):
      """
         sample this variable assuming parents and children given in x;
         in general, this is 
         
         P(self | x) = C P(children = x | self) P(self | parents = x)
         
         children of this class must decide the implementation
      """
      pass
      
      
   def children(self, network):
      if self.children_ is None:
         self.children_ = network.getChildren(self)
         self.children_ = sorted(self.children_, key=lambda x: VariableComparator(x))
      return self.children_ 
      
   def numFreeParameters(self):
      """The number of parameters that must be set for this variable"""
      return 1   
      
   def __eq__(self, x):
      return self.index == x.index

   def __ne__(self, x):
      return self.index != x.index

   def __str__(self):
      return str(self.index)

   def __repr__(self):
      return str(self.index)
   
   def _getExtraState(self):
      return None

   def __getstate__(self):
      extra = self._getExtraState()
      base = {
         'index': self.index, 
         'parentIndices': [parent.index for parent in self.parents]
      }
      base.update(extra)
      return base
   
   def __setstate__(self, state):
      self.__dict__.update(state)
      self.parents = []
      self.children_ = None
      
   @property
   def default(self):
      return 0.0
      
      
class VariableComparator(object):
   def __init__(self, obj):
      self.obj = obj
            
   def __lt__(self, v):
      return self.obj != v.obj and self.obj in v.obj.parents
      
   def __le__(self, v):
      return not self.__gt__(v)
      
   def __gt__(self, v):
      return self.obj != v.obj and v.obj in self.obj.parents
      
   def __ge__(self, v):
      return not self.__lt__(v)
      
   def __eq__(self, v):
      return self.obj == v.obj or self.__le__(v) and self.__ge__(v)
      
   def __ne__(self, v):
      return not self.__eq__(v)

class BinaryVariable(BayesVariable):
   def __init__(self, index):
      super(BinaryVariable, self).__init__(index)
      self.tables = {} # for each configuration, probability this variable is 1
      self.known = 0L
      self.epsilon = 1e-2
      
   def _getExtraState(self):
      return {
         'tables':self.tables,
         'known':self.known,
         'epsilon':self.epsilon
      }   
      
   def expand(self, x):
      """
         take a number and expand it to the known values
         the param has one entry per parent
         the param is a key to the probability table
         return is a bit string of size n (for a net with n nodes)  with values specified by x
         x is a representation whose length is the number of parents for this node
         return is a representation whose length is the number of nodes in the net
      """
      y = x
      ret = 0L
      for parent in self.parents:
         ret |= (y & 1L) << parent.index
         y >>= 1
      return ret
      
   def prob(self, xp):
       try:
          return self.tables[xp]
       except KeyError, msg:
          return self.epsilon
          
      
   def project(self, x):
      return x.base & self.known   
      
   def __call__(self, x):
      xp = self.project(x)
      p = self.prob(xp)
      x[self.index] = random.random_sample() <= p
      return x
      
   def isset(self, x):
      return ((1L << self.index) & x.known) != 0L   
      
   def density(self, x):
      xp = self.project(x)
      p = self.prob(xp)
      
      mask = 1L << self.index
      if x.known & mask == 0:
         return 1.0
      if x.base & mask:
         return p
      else:
         return 1. - p

   def marginalDensity(self, x, network):
      start = x[self.index]
      x[self.index] = True
      prod1 = self.density(x)
      for child in self.children(network):
         prod1 *= child.density(x)
      x[self.index] = False
      prod2 = self.density(x)
      for child in self.children(network):
         prod2 *= child.density(x)
      if prod1 == 0.0 and prod2 == 0.0:
         p = .5
      else:
         p = prod1 / (prod1 + prod2)
      x[self.index] = start
      if start:
         return p
      else:
         return 1. - p

   def marginal(self, x, network):
      x[self.index] = True
      prod1 = self.density(x)
      for child in self.children(network):
         prod1 *= child.density(x)
      x[self.index] = False
      prod2 = self.density(x)
      for child in self.children(network):
         prod2 *= child.density(x)
      if prod1 == 0.0 and prod2 == 0.0:
         p = .5
      else:
         p = prod1 / (prod1 + prod2)
      x[self.index] = random.random_sample() <= p
      return x
      
   def update(self, data):
      self.known = 0L
      for parent in self.parents:
         self.known |= 1L << parent.index
      self.tables = {}
      
      if data is None:
         # randomize the tables
         for cfg in self.configurations():
            if cfg.known == 0L and cfg.base == 0L:
               self.tables[self.project(cfg)] = random.random_sample()
            else:
               self.tables[self.project(cfg)] = random.binomial(1,.5,1) 
               #self.tables[self.project(cfg)] = random.beta(.5,.5) 
         return
      
      counts = {}
      for x in data:
         xp = self.project(x)
         mask = 1L << self.index
         if x.known & mask == 0 or x.known & self.known != self.known:
            continue
         
         match = x.base & mask != 0
         if self.tables.has_key(xp):
            if match:
               self.tables[xp] += 1.0
            counts[xp] += 1
         else:
            if match:
               self.tables[xp] = 2.0
            else:
               self.tables[xp] = 1.0
            counts[xp] = 2.0

      for xp in self.tables.keys():
         self.tables[xp] /= counts[xp]
      self.epsilon = 1.0 / (len(data) + 2.0)

   def values(self):
      mask = 1L << self.index
      yield TernaryString(0L, mask)
      yield TernaryString(mask, mask)
      raise StopIteration 

   def configurations(self):
      cnt = 1L << (len(self.parents))
      for i in xrange(cnt):
         yield TernaryString(self.expand(long(i)), self.known)
      raise StopIteration
   
   def numFreeParameters(self):
      return 1L << (len(self.parents) + 1)
   
   @property
   def default(self):
      return TernaryString(0L, 0L)
      

class MultinomialVariable(BayesVariable):
   def __init__(self, index, categories):
      super(MultinomialVariable, self).__init__(index)
      self.categories = categories # a list of lists of categories
      self.tables = {} # for each configuration, probability this variable is 1
      self.depth = len(self.categories[self.index]) - 1
      self.known = []
      self.epsilon = 1e-2
      self.data = None
      
   def _getExtraState(self):
      return {
         'categories':self.categories,
         'depth':self.depth,
         'tables':self.tables,
         'known':self.known,
         'epsilon':self.epsilon
      }   
      
   def expand(self, x):
      ret = zeros(len(self.categories), dtype=int)
      for i, parent in enumerate(self.parents):
         ret[parent.index] = x[i]
      return ret
      
   def prob(self, xp):
       """return a list of probabilities with length=self.depth"""
       try:
          return self.tables[xp]
       except KeyError, msg:
          #try:
          #   ret = self.queryData(xp)
          #   #print "probs: ", ret
          #   self.tables[xp] = ret
          #   return ret
          #except:
          return self.epsilon
          
      
   def project(self, x):
      """given an array of values map it to a lookup key"""
      return "".join([str(x[i]) for i in self.known])
      
   def __call__(self, x):
      xp = self.project(x)
      ps = self.prob(xp)
      r = random.random_sample()
      sum = 0.0
      for i,p in enumerate(ps):
         sum += p
         if r <= sum:
            x[self.index] = i+1
            break
      return x
      
   def isset(self, x):
      return x[self.index] >= 0   
      
   def density(self, x):
      xp = self.project(x)
      ps = self.prob(xp)
      val = x[self.index] - 1
      if val < 0: # missing or unknown value
         return 1.0
      elif val >= len(ps):
         return 1. - sum(ps)
      else:
         return ps[val]
 
   def marginalDensity(self, x, network):
      start = x[self.index]
      prods = []
      for i in xrange(self.depth + 1):
         x[self.index] = i + 1
         prod = self.density(x)
         for child in self.children(network):
            prod *= child.density(x)
         prods.append(prod)
      prods = array(prods)
      total = prods.sum()
      if total == 0.0:
         ps = 1./(self.depth+1) * ones(self.depth + 1)
      else:
         ps = prods / total
      x[self.index] = start
      return ps[start - 1]
 
   def marginal(self, x, network):
      prods = []
      for i in xrange(self.depth + 1):
         x[self.index] = i + 1
         prod = self.density(x)
         for child in self.children(network):
            prod *= child.density(x)
         prods.append(prod)
      prods = array(prods)
      total = prods.sum()
      if total == 0.0:
         ps = 1./(self.depth+1) * ones(self.depth)
      else:
         ps = prods[:-1] / total
      r = random.random_sample()
      sum = 0.0
      for i,p in enumerate(ps):
         sum += p
         if r <= sum:
            x[self.index] = i+1
            break
      return x
       
   def map(self,x):
      pmax = 0
      ymax = x
      initial = x
      initial[self.index] = 0;
      for y in self.values():
         p = self.density(initial + y)
         if p > pmax:
            pmax = p
            ymax = initial + y
      return ymax
      
   def update(self, data):
      if self.known is not None: del self.known
      if self.tables is not None: del self.tables
      if self.epsilon is not None: del self.epsilon
      self.known = []
      for parent in self.parents:
         self.known.append(parent.index)
      self.tables = {}
      
      if data is None:
         # randomize the tables
         for cfg in self.configurations():
            if (cfg == 0).all():
               self.tables[self.project(cfg)] = array([1. / (self.depth + 1) for i in xrange(self.depth)])
            else:
               index = random.randint(0, self.depth + 1)
               arr = zeros(self.depth)
               if index < self.depth:
                  arr[index] = 1.0
               self.tables[self.project(cfg)] = arr 
         return
      
      """
      self.data = data
      self.dataProc = {}
      for x in data:
         xp = self.project(x)
         if self.dataProc.has_key(xp):
            self.dataProc[xp].append(x[self.index])
         else:
            self.dataProc[xp] = [x[self.index]]
      """
      
      counts = {}
      for x in data:
         skip = x[self.index] == 0
         for i in self.known:
            if x[i] == 0:
               skip = True
               break
         if skip: continue
         
         xp = self.project(x)
         
         val = x[self.index] - 1
         incr = zeros(self.depth)
         if val < self.depth:
            incr[val] = 1
         if self.tables.has_key(xp):
            self.tables[xp] += incr
            counts[xp] += 1
         else:
            self.tables[xp] = ones(self.depth) + incr
            counts[xp] = self.depth + 2

      for xp in self.tables.keys():
         self.tables[xp] /= counts[xp]
      
      self.epsilon = array([1.0 / (len(data) + self.depth + 1) for i in xrange(self.depth)])

   def queryData(self, xp):
      """
         calculate the probability for this entry on the fly 
         given the projection
      """
      count = self.depth + 1
      probs = ones(self.depth + 1)
      for y in self.dataProc[xp]:
         val = y - 1 
         probs[val] += 1
         count += 1
      return probs[:-1] / count
            
            

   def values(self):
      for i in xrange(self.depth + 1):
         ret = zeros(len(self.categories), dtype=int)
         ret[self.index] = i + 1
         yield ret
         del ret   
      raise StopIteration 

   def configurations(self):
      index = 0
      value = 0
      current = ones(len(self.parents), dtype=int)
      while index < len(self.parents):
         next = self.expand(current)
         yield next
         del next
         current[index] += 1
         while current[index] > len(self.categories[self.parents[index].index]):
            current[index] = 1
            index += 1
            current[index] += 1
      raise StopIteration
   
   def numFreeParameters(self):
      prod = 1
      for parent in self.parents:
         prod *= parent.depth + 1
      return prod * self.depth
   
   @property
   def default(self):
      return zeros(len(self.categories), dtype=int)
      
class MultinomialVariableGenerator(object):
   def __init__(self, categories):
      self.categories = categories

   def __call__(self, index):
      return MultinomialVariable(index, self.categories)

class RealVariable(BayesVariable):
   pass

class GaussianVariable(RealVariable):
   def __init__(self, index, dim, scale):
      super(GaussianVariable, self).__init__(index)
      self.mu = zeros(1)
      self.sd = zeros((1,1))
      self.sdinv = zeros((1,1))
      self.dim = dim
      self.scale = scale
      
   def _getExtraState(self):
      return {
        'mu':self.mu,
        'sd':self.sd,
        'sdinv':self.sdinv,
        'dim':self.dim,
        'scale':self.scale
      }

   def density(self, x):
      """get the density for vector x"""
      y = x[self.index]
      mu = self.mean(x)
      sd = self.stddev(x)
      return  nan_to_num(exp(-((y - mu)**2) / (2 * (sd ** 2))) / (sd * sqrt(2 * pi)))

   def __call__(self, x):
      """sample the variable, conditional on x"""
      #print "Gaussian Sample"
      mu = self.mean(x)
      sd = self.stddev(x)
      x[self.index] = float(mu + random.randn(1) * sd)
      #print mu, sd, self.mu, self.sdinv[:,0], x[self.index]
      #print "end Gaussian Sample"
      return nan_to_num(x)


   def mean(self, x):
      """compute the mean based on the values in x"""
      xp = self.project(x)
      # print "mean: ", self.sd[0,1:], 1./self.sdinv[1:,0]
      num = (xp[1:] - self.mu[1:]) * self.sdinv[1:,0]
      m = self.mu[0] - nan_to_num(num.sum() / (self.sdinv[0, 0]) ) 
      if abs(m) > self.scale:
         if m < self.scale:
            return -self.scale
         else:
            return self.scale
      return m
 
   def stddev(self, x):
      # print "stddev: ", self.sdinv[0,0], 1. / sqrt(self.sdinv[0,0]), sqrt(self.sd[0,0])
      
      sd =  sqrt(self.sd[0,0])
      if sd > self.scale:
         return self.scale
      elif sd == 0.0:
         return 1.0
      return sd

   def update(self, data):
      #print "update"
      #for x in data:
      #   print x
      sz = 1 + len(self.parents)
      
      if data is None:
         # randomize
         self.mu = random.randn(sz)
         self.sd = random.randn(sz,sz)
      else:
         self.mu = zeros(sz)
         self.sd = zeros((sz,sz))
      
         data2 = [nan_to_num(self.project(x)) for x in data]
         for x in data2:
            self.mu += x
         self.mu /= len(data)
         for x in data2:
            for y in data2:
               self.sd += nan_to_num(outer(x, y))
         self.sd /= len(data) - 1
         self.sd -= outer(self.mu, self.mu)
         #print "updated"
         #print self.mu
         #print self.sd
      try:
         self.sdinv = numpy.linalg.inv(self.sd)
      except:
         try:
            m = self.sd.min()
            sd = self.sd / m
            sd = sd.round(decimals=10) * m
            self.sdinv = numpy.linalg.inv(sd)
         except:   
            print "singular", ','.join([str(parent.index) for parent in self.parents])
            print '[[', float(self.sd[0,0]),',', float(self.sd[0,1]), '],[', float(self.sd[1,0]),',',float(self.sd[1,1]),']]'
         
            print self.sd
            raise
      #print self.sdinv
      #print dot(self.sd, self.sdinv)
      #print "end update"
         
   @property
   def default(self):
      return zeros(self.dim)
