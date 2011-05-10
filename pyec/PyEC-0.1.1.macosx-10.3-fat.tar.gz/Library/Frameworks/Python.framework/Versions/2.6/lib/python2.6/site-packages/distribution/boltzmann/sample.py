from numpy import *
from pyec.util.TernaryString import TernaryString
from pyec.distribution.basic import BernoulliTernary
import struct, binascii

class BoltzmannSampler(object):
   def batch(self, rbm, size, initial, useAlternate=False):
      return self.__call__(rbm, size, initial, useAlternate)
   
   
class RBMGibbsSampler(BoltzmannSampler):
   def __init__(self, burn, chains):
      self.burn = burn
      self.chains = chains
      
   def __call__(self, rbm, size=1, initial=None, useAlternate=False, clampIdx=None):
      from pyec.util.TernaryString import TernaryString
      sample = []
      vsize = rbm.vsize
      hsize = rbm.hsize
      if useAlternate:
         w = rbm.wg
         bv = rbm.bvg
         bh = rbm.bhg
      else:
         w = rbm.w
         bv = rbm.bv
         bh = rbm.bh
      if clampIdx is None:
         clampIdx = 0
      if initial is not None:
         initialArr = initial.toArray(rbm.dim)
      for i in xrange(self.chains):
         if initial is not None:
            x = initialArr
         else:
            x = random.random_sample(vsize+hsize).round()
         for j in xrange(self.burn + size / self.chains):
            v = dot(w, x[vsize:]) + bv
            x[clampIdx:vsize] = random.binomial(1, 1. / (1. + exp(-v/(100 - j))), vsize)[clampIdx:]
            h = dot(x[:vsize], w) + bh
            x[vsize:] = random.binomial(1, 1. / (1. + exp(-h/(100 - j))), hsize)
            if j >= self.burn:
               sample.append(TernaryString.fromArray(x))
      return sample

class RBMSwendsonWangSampler(BoltzmannSampler):
   def __init__(self, burn, chains):
      self.burn = burn
      self.chains = chains
      
   def __call__(self, size=1, initial = None, useAlternate=False):
      from pyec.util.TernaryString import TernaryString
      sample = []
      vsize = rbm.vsize
      hsize = rbm.hsize
      if useAlternate:
         w = rbm.wg
         bv = rbm.bvg
         bh = rbm.bhg
      else:
         w = rbm.w
         bv = rbm.bv
         bh = rbm.bh
      
      if initial is not None:
         initialArr = initial.toArray(rbm.dim)
      start = time()
      for n in xrange(self.chains):
         start = time()
         if initial is not None:
            x = initialArr
         else:
            x = random.random_sample(vsize + hsize).round()
         last = copy(x)
         repeats = 0
         for l in xrange(self.burn + size / self.chains):
            startInner = time()
            clusters = {}
            for i in xrange(vsize):
               for j in xrange(hsize):
                  i2 = j + vsize
                  if (w[i,j] < 0.0 and x[i] != x[i2] and random.random_sample() < 1. - exp(2 * w[i,j])) or \
                   (w[i,j] > 0.0 and x[i] == x[i2] and random.random_sample() < 1. - exp(-2 * w[i,j])):
                  #if d[i,j] > 0.0:
                     si = [i]
                     sj = [i2]
                     if clusters.has_key(i):
                        si = clusters[i]
                     if clusters.has_key(i2):
                        sj = clusters[i2]
                     s = list(set(si + sj))
                     for k in s:
                        clusters[k] = s
            
            computed = zeros(x.size)
            for k, s in clusters.iteritems():
               if computed[k] > 0.0:
                  continue
               bias = 0.0
               for m in s:
                  if m >= vsize:
                     bias += bh[m - vsize]
                  else:
                     bias += bv[m]
               state = float(random.binomial(1, 1. / (1. + exp(-bias)), 1))
               for m in s:
                  x[m] = state
                  computed[m] = 1.0
                  
            for i in xrange(x.size):
               if computed[i] < 1.0:
                  i2 = i
                  b = bv
                  if i2 >= vsize:
                     i2 -= vsize
                     b = bh
                  x[i] = float(random.binomial(1, 1. / (1. + exp(-b[i2])), 1))
            if l >= self.burn:
               sample.append(TernaryString.fromArray(x))
         print "SW sample ", n, ": ", time() - start   
         
      return sample    
      
class RBMSimulatedTempering(BoltzmannSampler):
   def __init__(self, burn, chains = 1, temps = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]):
      self.burn = burn
      self.chains = chains
      self.temps = array(temps)
      self.steps = array([i+1. for i in xrange(len(temps))])
      self.weights = None
      ps = self.temps[:-1] / self.temps[1:]
      self.pdown =  ps[:-1]/ ps[:-1] + ps[1:]
      self.pdown = append(zeros(1), self.pdown, axis=0)
      self.pdown = append(self.pdown, zeros(1), axis=0)
   
   def mutate(self, rbm, x, idx):
      numBytes = int(ceil(rbm.dim / 8.0))
      numFull  = rbm.dim / 8
      initial = ''
      if numBytes != numFull:
         extra = rbm.dim % 8
         initMask = 0
         for i in xrange(extra):
            initMask <<= 1
            initMask |= 1
         initial = struct.pack('B',initMask)
      
      start = (1L << (rbm.dim + 1)) - 1
      p = self.steps[idx] / rbm.dim
      base = 0L
      while p > 1e-16:
         reps = int(-floor(log2(p)))
         q = 2.0 ** -reps
         next = start
         for i in xrange(reps):
            next &= long(binascii.hexlify(random.bytes(numBytes)), 16) 
         base |= next
         p = (p - q) / (1.0 - q)   
      
      base = x.base & ~base | ~x.base & base
      known = x.known# long(binascii.hexlify(initial + '\xff'*numFull), 16)
      return TernaryString(base, known)   
            
   def __call__(self, rbm, size=1, initial = None, useAlternate=False):
      sample = []
      uniform = BernoulliTernary(rbm)
      if self.weights is None:
         wsample = uniform.batch(10000)
         self.weights = []
         base = array([exp(-rbm.energy(x, useAlternate)) for x in wsample]) 
         for temp in self.temps:
            self.weights.append(((base ** (1. / temp)) / 10000.).sum())
      
      
      for n in xrange(self.chains):
         # initialize the chain
         x = uniform()
         idx = 1
         for l in xrange(self.burn + size / self.chains):
            y = self.mutate(rbm, x, idx)
            
            ratio = exp((rbm.energy(x, useAlternate)-rbm.energy(y,useAlternate)) / self.temps[idx]) 
            if random.random_sample() < ratio:
               x = y
            
            if random.random_sample() < self.pdown[idx]:
               idx2 = idx - 1
               p1 = 1 - self.pdown[idx2]
               p2 = self.pdown[idx]
            else:
               idx2 = idx + 1
               p1 = self.pdown[idx2]
               p2 = 1. - self.pdown[idx]
            e1 = exp(-rbm.energy(x, useAlternate) / self.temps[idx]) * p1 * self.weights[idx]
            e2 = exp(-rbm.energy(x, useAlternate) / self.temps[idx2]) * p2 * self.weights[idx2]
            if random.random_sample() < e2 / e1:
               idx = idx2 
            if l >= self.burn:
               sample.append(x)
      return sample
         
      
      
