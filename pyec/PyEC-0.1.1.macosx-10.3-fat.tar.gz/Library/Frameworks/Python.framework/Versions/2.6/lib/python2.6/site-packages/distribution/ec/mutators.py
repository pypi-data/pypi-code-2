from numpy import *
from pyec.util.TernaryString import TernaryString
import copy, binascii, struct
from pyec.distribution.basic import PopulationDistribution
from pyec.db.models import Segment, Partition

class Crosser(object):
   """ given a list of organisms, perform recombination"""
   def __call__(self, orgs, prob):
      return orgs[0]

class UniformCrosser(Crosser):
   def __call__(self, orgs, prob):
      if random.random_sample() > prob:
         return orgs[0]
      if isinstance(orgs[0], ndarray):
         rnd = random.random_sample(len(orgs[0])).round()
         return rnd * orgs[0] + (1 - rnd) * orgs[1]
      elif isinstance(orgs[0], TernaryString):
         rnd = random.bytes(len(str(orgs[0])) * 8)
         rnd = long(binascii.hexlify(rnd), 16)
         base = rnd & orgs[0].base | ~rnd & orgs[1].base
         known = rnd & orgs[0].known | ~rnd & orgs[1].known
         return TernaryString(base, known)
      else:
         return None

class OnePointCrosser(Crosser):
   def __call__(self, orgs, prob=1.0):
      if random.random_sample() > prob:
         return orgs[0]
      idx = random.random_integers(0, len(orgs[0]) - 1)
      return append(orgs[0][:idx], orgs[1][idx:], axis=0)
      
class TwoPointCrosser(Crosser):
   def __call__(self, orgs, prob=1.0):
      if random.random_sample() > prob:
         return orgs[0]
      idx1 = random.random_integers(0, len(orgs[0]) - 1)
      idx2 = idx1
      while idx1 == idx2:
         idx2 = random.random_integers(0, len(orgs[0]) - 1)
    
      if idx1 > idx2:
         a = idx1
         idx1 = idx2
         idx2 = a

      return append(append(orgs[0][:idx1], orgs[1][idx1:idx2],axis=0), orgs[0][idx2:], axis=0)


class IntermediateCrosser(Crosser):
   def __call__(self, orgs, prob=1.0):
      return array(orgs).sum(axis=0) / len(orgs)
      
class DominantCrosser(Crosser):
   def __call__(self, orgs, prob=1.0):
      x = []
      for i in xrange(len(orgs[0])):
         idx = random.randint(0, len(orgs) - 1)
         x.append(orgs[idx][i])
      return array(x)
      
class DifferentialCrosser(Crosser):
   def __init__(self, learningRate, crossoverProb):
      self.CR = crossoverProb
      self.F = learningRate

   def __call__(self, orgs, prob=1.0):
      y, a, b, c = orgs
      d = random.randint(0, len(y))
      idx2 = 0
      for yi in y:
         r = random.random_sample()
         if idx2 == d or r < self.CR:
            y[idx2] = a[idx2] + self.F * (b[idx2] - c[idx2]) 
            idx2 += 1
      return y

class Mutation(PopulationDistribution):
   def __init__(self, config):
      super(Mutation, self).__init__(config)
      self.population = None
   
   def mutate(self, x):
      return x

   def batch(self, popSize):
      pop = []
      for x,s in self.population:
         z = self.mutate(x)
         if isinstance(z, ndarray):
            while (abs(z - self.config.center) > self.config.scale).any():
               z = self.mutate(x)
         pop.append(z)
      return pop
   
   def update(self, generation, population):
      self.population = population

class Crossover(Mutation):
   def __init__(self, selector, crossFunc, order=2):
      super(Crossover, self).__init__(selector.config)
      self.selector = selector
      self.crosser = crossFunc
      self.order = order
      self.n = 1
   
   def mutate(self, x):
      raise Exception, "Operation not supported"   
            
   def batch(self, popSize):
      crossoverProb = hasattr(self.config, 'crossoverProb') and self.config.crossoverProb or 1.0
      if crossoverProb < 1e-16:
         return [x for x,s in self.population1]
      if hasattr(self.config, 'passArea') and self.config.passArea:
         pops = [[x[0] for x,s in self.population1]]
         areas = [x[1] for x,s in self.population1]
         crossoverProb *= array(areas) ** (1. / self.config.dim)
      else:
         pops = [[x for x,s in self.population1]]
         crossoverProb = crossoverProb * ones(popSize) * sqrt(1./self.n)
      for i in xrange(self.order - 1):
         if hasattr(self.config, 'passArea') and self.config.passArea:
            pops.append([x[0] for x in self.selector.batch(popSize)])
         else:
            pops.append(self.selector.batch(popSize))
      pops.append(list(crossoverProb))
      if hasattr(self.config, 'passArea') and self.config.passArea:
         return zip([self.crosser(orgs[:-1], orgs[-1]) for orgs in zip(*pops)], areas)
      else:
         return [self.crosser(orgs[:-1],orgs[-1]) for orgs in zip(*pops)]
   
   def update(self, generation, population):
      self.n = generation
      self.population1 = copy.deepcopy(population)
      # self.selector should already be updated, update is called to give us
      # the selected result

class Gaussian(Mutation):
   def __init__(self, config):
      super(Gaussian, self).__init__(config)
      self.sd = config.stddev
      
   def mutate(self, x):
      return x + random.randn(len(x)) * self.sd

class DecayedGaussian(Gaussian):
   def update(self, generation, population):
      super(DecayedGaussian, self).update(generation, population)
      self.sd = self.config.varInit * exp(-(generation * self.config.varDecay) ** self.config.varExp) 

class AreaSensitiveGaussian(Mutation):
   sdavg = 0
   sdcnt = 0
   sdmin = 1e100
   def mutate(self, x):
      y = x[0]
      area = x[1]
      # sd = 2 * self.config.scale / (-log(area))
      sd = self.config.varInit * self.config.scale * (area ** (1./len(y)))
      self.sdavg = (self.sdavg * self.sdcnt + sd) / (self.sdcnt + 1.0)
      self.sdcnt += 1
      self.sdmin = (sd < self.sdmin) and sd or self.sdmin
      ret = y + random.randn(len(y)) * sd
      for i, val in enumerate(abs(ret - self.config.center) > self.config.scale):
         if val:
            while abs(ret[i] - self.config.center) > self.config.scale:
               ret[i] = y[i] + random.randn(1) * sd
      return ret

   def update(self, generation, population):
      super(AreaSensitiveGaussian, self).update(generation, population)
      self.sdcnt = 0
      self.sdavg = 0.0
      self.sd = self.sdmin
      self.sdmin = 1e100

class UniformArea(Mutation):
   segment = None
   sd = 1.0
   def mutate(self, x):
      node, lower, upper = Partition.objects.traversePoint(self.segment.id, x, self.config)
      self.sd = (node.area < self.sd) and node.area or self.sd
      r = random.random_sample(len(x))
      return lower + r * (upper - lower)
      
   def update(self, n, population):
      super(UniformArea, self).update(n, population)
      if self.segment is None:
         self.segment = Segment.objects.get(name=self.config.segment)

class Cauchy(Mutation):
   def __init__(self, config):
      super(Cauchy, self).__init__(config)
      self.sd = config.stddev

   def mutate(self, x):
      return x + random.standard_cauchy(len(x))

class DecayedCauchy(Cauchy):
   def update(self, generation, population):
      super(DecayedGaussian, self).update(generation, population)
      self.sd = self.config.varInit * exp(-(generation * self.config.varDecay) ** self.config.varExp) 
      
class Bernoulli(Mutation):
   def __init__(self, config):
      super(Bernoulli, self).__init__(config)
      self.bitFlipProbs = .5
      if hasattr(config, 'bitFlipProbs'):
         self.bitFlipProbs = config.bitFlipProbs

   def mutate(self, x):
      numBytes = int(ceil(self.config.dim / 8.0))
      numFull  = self.config.dim / 8
      initial = ''
      if numBytes != numFull:
         extra = self.config.dim % 8
         initMask = 0
         for i in xrange(extra):
            initMask <<= 1
            initMask |= 1
         initial = struct.pack('B',initMask)
      
      start = (1L << (self.config.dim + 1)) - 1
      p = self.bitFlipProbs
      if (isinstance(p, ndarray) and (p > 1.0).any()) or (not isinstance(p, ndarray) and p > 1.0): raise Exception, "bit flip probability > 1.0: " + str(p)
      base = 0L
      active = TernaryString(x.known,x.known)
      while (isinstance(p, ndarray) and (p > 1e-16).any()) or (not isinstance(p, ndarray) and p > 1e-16):
         #print p
         reps = minimum(100, -floor(maximum(log2(p), 0.0)))
         #print p, reps
         q = 2.0 ** -reps
         next = start
         activeReps = TernaryString(active.base, active.known)
         if isinstance(p, ndarray):
            for j, pj in enumerate(p):
               if pj < 1e-16:
                  active[j] = False
            #print "active: ", active.toArray(p.size)
            for i in xrange(int(max(reps))):
               for j,r in enumerate(reps):
                  if i >= r:
                     activeReps[j] = False
               #print "activeReps: ", activeReps.toArray(p.size)
               next &= activeReps.base & long(binascii.hexlify(random.bytes(numBytes)), 16)
         else:
            for i in xrange(int(reps)):
               next &= long(binascii.hexlify(random.bytes(numBytes)), 16) 
         base |= next & active.base
         p = (p - q) / (1.0 - q)
            
      
      base = x.base & ~base | ~x.base & base
      known = x.known# long(binascii.hexlify(initial + '\xff'*numFull), 16)
      return TernaryString(base, known)



class DecayedBernoulli(Bernoulli):
   def update(self, generation, population):
      super(DecayedBernoulli, self).update(generation, population)
      self.bitFlipProbs = self.config.varInit * exp(-(generation * self.config.varDecay) ** self.config.varExp) 

class AreaSensitiveBernoulli(Bernoulli):
   bfavg = 0
   bfcnt = 0
   bfmin = 1e100
   
   def density(self, x, z):
      y = x[0]
      area = x[1]
      bf = self.config.varInit / (-log(area))
      prod = 1.0
      for i in xrange(self.config.dim):
         if z[i] != y[i]:
            prod *= bf
         else:
            prod *= (1. - bf)
      return prod
      
   def mutate(self, x):
      y = x[0]
      area = x[1]
      bf = self.config.varInit / (-log(area))
      #bf = .2 ** (-log(area)/self.config.rawdim)
      self.bfavg = (self.bfavg * self.bfcnt + bf) / (self.bfcnt + 1.0)
      self.bfcnt += 1
      self.bfmin = (bf < self.bfmin) and bf or self.bfmin
      self.bitFlipProbs = minimum(bf, 1.0)
      return super(AreaSensitiveBernoulli, self).mutate(y)

   def update(self, generation, population):
      super(AreaSensitiveBernoulli, self).update(generation, population)
      self.bitFlipProbs = self.bfavg
      self.bfmin = 1e100
      self.bfcnt = 0
      self.bfavg = 0.0

class UniformAreaBernoulli(Bernoulli):
   segment = None
   bitFlipProbs = 1.0
   def mutate(self, x):
      node, lower, upper = Partition.objects.traversePoint(self.segment.id, x[0], self.config)
      #print node.id, lower, upper
      #bitFlipProbs = (upper - lower) * .5
      self.bitFlipProbs = maximum(((upper - lower) > .75) * .5 * self.config.varInit,self.config.varInit / (-log(x[1]))) 
      #print self.bitFlipProbs
      self.sd = .1/-log(x[1])
      ret = super(UniformAreaBernoulli, self).mutate(x[0])
      #print "x: ", x[0]
      #print "y: ", ret
      return ret
      
   def update(self, n, population):
      super(UniformAreaBernoulli, self).update(n, population)
      if self.segment is None:
         self.segment = Segment.objects.get(name=self.config.segment)      
      
class EndogeneousGaussian(Mutation):
   def __init__(self, config):
      super(EndogeneousGaussian, self).__init__(config)
      self.sd = config.varInit
      self.dim = config.dim
      self.scale = config.scale
      self.bounded = config.bounded
      self.tau = self.sd / sqrt(2*sqrt(config.populationSize))
      self.tau0 = self.sd / sqrt(2*config.populationSize)
      self.numEndogeneous = self.dim
   
   def mutate(self, x):
      z = 2 * self.scale * ones(self.dim)
      while (abs(z) > self.scale).any():
         y = x[:self.dim]
         sig = x[self.dim:]
         rnd = self.tau * random.randn(len(sig))
            
         sig2 = exp(self.tau0 * random.randn(1)) * sig * exp(rnd) 
         z = y + sig2 * random.randn(len(y))
         if not self.bounded:
            break
      return append(z, sig2, axis=0) 
      
   

class CorrelatedEndogeneousGaussian(Mutation):
   def __init__(self, config):
      super(CorrelatedEndogeneousGaussian,self).__init__(config)
      self.sd = config.varInit
      self.dim = config.dim
      self.center = config.center
      self.scale = config.scale
      self.bounded = config.bounded
      self.cumulation = config.cmaCumulation
      self.cu = sqrt(self.cumulation * (2 - self.cumulation))
      self.beta = config.cmaDamping
      self.chi = sqrt(config.populationSize) \
       * (1. - (1./(4*config.populationSize)) \
          + (1./(21 * (config.populationSize ** 2))))
      self.correlation = config.cmaCorrelation
      self.numEndogeneous = self.dim * (self.dim - 1) / 2 + 3*self.dim
    
   def unpack(self, sig):
      """take a N(N-1)/2 array and make a N x N matrix"""
      idx = 0
      mat = []
      for i in xrange(self.dim):
         row = []
         for j in xrange(self.dim):
            if j < i:
                row.append(0)
            else:
                row.append(sig[idx])
                idx += 1
         mat.append(row)
      return array(mat)
   
   def pack(self, mat):
      """take a N x N matrix and make a N(N-1)/2 array"""
      idx = 0
      sig = []
      for i in xrange(self.dim):
         for j in xrange(self.dim):
            if j >= i:
                sig.append(mat[i][j])
      return array(sig) 
   
   def mutate(self, x):
      z = 2 * self.scale * ones(self.dim) + self.center
      y = x[:self.dim]
      sig = x[self.dim:-3*self.dim]
      cum = x[-3*self.dim:-2*self.dim]
      delta = x[-2*self.dim:-self.dim]
      deltaCum = x[-self.dim:]
      rot = self.unpack(sig)
      corr = dot(rot, rot)
            
      deltaRot = rot / outer(rot.sum(axis=1), ones(self.dim))
      while (abs(z - self.center) > self.scale).any():
         deltaCum2 = (1 - self.cumulation) * deltaCum \
          + self.cu * dot(deltaRot, random.randn(self.dim))
         delta2 = delta * exp(self.beta * (sqrt(deltaCum2 ** 2) - self.chi))
            
         cum2 = (1 - self.cumulation) * cum \
          + self.cu * dot(rot, random.randn(self.dim))
         corr2 = (1 - self.correlation) * corr \
          + self.correlation * outer(cum2, cum2)
         rot2 = linalg.cholesky(corr2)
         sig2 = self.pack(rot2)
            
                        
         z = y + delta * dot(rot, random.randn(len(y)))
            
         if not self.bounded:
            break
      z0 = append(append(z, sig2, axis=0), cum2, axis=0)
      z1 = append(append(z0, delta2, axis=0), deltaCum2, axis=0)
      self.sd = average(sig)
      return z1   
            
