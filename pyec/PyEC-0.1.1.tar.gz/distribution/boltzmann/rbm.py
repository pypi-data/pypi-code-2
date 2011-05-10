from numpy import *
from pyec.distribution.basic import Distribution
from pyec.util.TernaryString import TernaryString
from time import time
from sample import *

class rbm(Distribution):
   """ a binary rbm """
   center = 0.5
   scale = 0.5
   
   def __init__(self, vsize, hsize, lr=0.01, mo=0.9):
      self.vsize = vsize
      self.hsize = hsize
      self.dim = vsize + hsize
      self.rate = lr
      self.momentum = mo
      self.w = random.standard_cauchy((vsize, hsize)) / vsize / hsize
      self.bv = random.standard_cauchy(vsize) / vsize / hsize
      self.bh = random.standard_cauchy(hsize) / hsize / vsize
      self.wc = zeros((vsize,hsize))
      self.bvc = zeros(vsize)
      self.bhc = zeros(hsize)
      self.wg = copy(self.w)
      self.bvg = copy(self.bv)
      self.bhg = copy(self.bh)
      self.wcg = zeros((vsize,hsize))
      self.bvcg = zeros(vsize)
      self.bhcg = zeros(hsize)
      self.sampler = RBMSimulatedTempering(1000)
      self.samplerAlt = RBMSimulatedTempering(1000)
      
      
   def __call__(self, x):
      return self.energy(x)   
      
   def energy(self, x, useAlternate=False):
      """ compute the energy function """
      if useAlternate: return self.energy2(x)
      v = x[:self.vsize].toArray(self.vsize)
      h = x[self.vsize:self.vsize+self.hsize].toArray(self.hsize)
      ret = -(dot(v, dot(self.w, h)) + dot(v, self.bv) + dot(h, self.bh))
      return ret
   
   def energy2(self, x):
      """ compute the energy function """
      v = x[:self.vsize].toArray(self.vsize)
      h = x[self.vsize:self.vsize+self.hsize].toArray(self.hsize)
      ret = -(dot(v, dot(self.wg, h)) + dot(v, self.bvg) + dot(h, self.bhg))
      return ret
   
   def partition(self):
      """ compute the partition function - only for small dimension !!! """
      from pyec.util.TernaryString import TernaryString
      total = 0
      vsize = self.vsize
      hsize = self.hsize
      all = (1L << (vsize+hsize)) - 1L
      for i in xrange(1 << (vsize+hsize)):
         total += exp(self.__call__(TernaryString(long(i), all)))
      return total
   
   def scoreSample(self, sample, Z=1.0):
      return [(x, exp(-self.__call_(x))/Z) for x in sample]
   
   def batch(self, size):
      return self.sampler(self, size)
      

                           
   def bucket(self, sample, Z=1.0):
      """build a dictionary containing a histogram"""
      d = {}
      size = len(sample)
      incr = 1.0 / size
      for x in sample:
         y = str(x)
         if d.has_key(y):
            d[y][0] += incr
         else:
            d[y] = [incr, exp(-self.__call__(x))/Z]
      return d

   def complete(self, data):
      completed = []
      for v in data:
         x = zeros(self.vsize + self.hsize)
         x[:self.vsize] = v
         h = dot(v, self.w) + self.bh
         x[self.vsize:] = 1. / (1. + exp(-h))
         completed.append(TernaryString.fromArray(x))
      return completed
   
   def complete2(self, data):
      completed = []
      for v in data:
         x = zeros(self.vsize + self.hsize)
         x[:self.vsize] = v
         h = dot(v, self.wg) + self.bhg
         x[self.vsize:] = 1. / (1. + exp(-h))
         completed.append(TernaryString.fromArray(x))
      return completed
         
   def correlate(self, data):
      ws = zeros((self.vsize, self.hsize))
      vs = zeros(self.vsize)
      hs = zeros(self.hsize)
      for d in data:
         x = d.toArray(self.vsize + self.hsize)
         v = x[:self.vsize]
         h = x[self.vsize:]
         ws += outer(v,h) / len(data)
         vs += v / len(data)
         hs += h / len(data)
      return ws, vs, hs

   def train(self):
      completed = self.complete(self.data)
      energy = sum([self.energy(d) for d in completed]) / len(completed)
      c2 = self.complete2(self.data)
      energy2 = sum([self.energy2(d) for d in c2]) / len(c2) 
      print "Energy of data: ", energy, " v ", energy2, "\n\n"
      sampled = self.sampler.batch(len(self.data))
      g = self.samplerAlt.batch(self, len(self.data), None, True)
      energy = sum([self.energy(d) for d in sampled]) / len(sampled)
      energy2 = sum([self.energy2(d) for d in g]) / len(g) 
      print "Energy of sample: ", energy, " v ", energy2
      dw, dv, dh = self.correlate(completed)
      mw, mv, mh = self.correlate(sampled)
      self.wc += (1 - self.momentum) * self.rate * (dw - mw)
      self.bvc += (1 - self.momentum) * self.rate * (dv - mv)
      self.bhc += (1 - self.momentum) * self.rate * (dh - mh)
      self.w += self.wc
      self.bv += self.bvc
      self.bh += self.bhc
      self.wc *= self.momentum
      self.bhc *= self.momentum
      self.bvc *= self.momentum
      
      gw, gv, gh = self.correlate(g)
      dw, dv, dh = self.correlate(c2)
      self.wcg += (1 - self.momentum) * self.rate * (dw - gw)
      self.bvcg += (1 - self.momentum) * self.rate * (dv - gv)
      self.bhcg += (1 - self.momentum) * self.rate * (dh - gh)
      self.wg += self.wc
      self.bvg += self.bvc
      self.bhg += self.bhc
      self.wcg *= self.momentum
      self.bhcg *= self.momentum
      self.bvcg *= self.momentum
      
      self.sampler.completeTraining(self)
         
