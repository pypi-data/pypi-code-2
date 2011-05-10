from numpy import *
import binascii, struct
from pyec.config import Config, ConfigBuilder
from pyec.util.registry import BENCHMARKS
from pyec.util.TernaryString import TernaryString

class Distribution(object):
   """A Distribution that can be sampled"""

   def __init__(self, config):
      super(Distribution, self).__init__()
      self.config = config

   def __call__(self, **kwargs):
      """Get a single sample from the distribution"""
      return self.batch(1)

   def batch(self, sampleSize):
      """Get a sample from the distribution"""
      pass

class ProposalDistribution(Distribution):
   """A proposal distribution for simulated annealing"""

   def adjust(self, rate):
      """given the current acceptance rate, alter the distribution as needed"""
      pass

   def densityRatio(self, x1, x2, i=None):
      """given two points, give the ratio of the densities p(x1) / p(x2)"""
      pass

class PopulationDistribution(Distribution):
   """A distribution governing a population algorithm"""

   def update(self, n, population):
      """
         Update the distribution with the latest population
          
         population is a list of (point, score) tuples

         If config.sorted is True, the list will be sorted by descending score.
      """
      pass

   def run(self, segment='test', fitness=None, **kwargs):
     from pyec.trainer import Trainer
     if fitness is None:
        fitness = BENCHMARKS.load(self.config.function)
     self.config.segment = segment
     self.config.center = fitness.center
     self.config.scale = fitness.scale
     self.config.fitness = fitness
     fitness.algorithm = self
     if hasattr(fitness, 'initial'):
        self.config.initialDistribution = fitness.initial
     trainer = Trainer(fitness, self, **kwargs)
     trainer.train()
     return fitness

   def convert(self, x):
      """ 
         Convert a point to a scorable representation
         
         x - the candidate solution
      """
      return x

   @classmethod
   def configure(cls, generations, populationSize, dimension=1, function=None):
      """
         Return a Config object
      """
      return cls.configurator().configure(generations, populationSize, dimension, function)
      
   @classmethod
   def configurator(cls):
      """
         Return a ConfigurationBuilder
      """
      return ConfigBuilder()

class Gaussian(ProposalDistribution):
   def __init__(self, config):
      super(Gaussian, self).__init__(config)
      self.dim = config.dim
      self.bounded = config.bounded
      self.var = 1.
      if hasattr(config, 'varInit'):
         self.var = config.varInit
      self.varIncr = 1.05
      self.usePrior = config.usePrior

   def __call__(self, **kwargs):
      center = zeros(self.dim)
      if self.usePrior and kwargs.has_key('prior'):
         center = kwargs['prior']
      # vary the mixture point
      var = self.variance()
      if kwargs.has_key('idx') and hasattr(var, '__len__'):
         var = var[kwargs['idx']]
      varied = random.randn(self.dim) * var + center
      
      
      # check bounds; call again if outside bounds
      if self.bounded:
         try:
            if (abs(varied - self.config.center) > self.config.scale).any():
               return self.__call__(**kwargs)
         except RuntimeError, msg:
            print "Recursion error: ", varied
            print abs(varied - self.config.center)
            print self.config.scale
      return varied

   def batch(self, popSize):
      return [self.__call__(idx=i) for i in xrange(popSize)]
         
   def variance(self):
      return self.var
            
   def adjust(self, rate):
      if not hasattr(rate, '__len__'):
         if rate < .23:
            self.var /= self.varIncr
         else:
            if self.var < self.config.scale / 5.:
               self.var *= self.varIncr
         return
      self.var = self.var * ones(len(rate))
      for i in  xrange(len(rate)):
         if rate[i] < .23:
            self.var[i] /= self.varIncr
         else:
            if self.var[i] < self.config.scale / 5.:
               self.var[i] *= self.varIncr
      # print rate, self.var

   def densityRatio(self, x1, x2, i = None):
      if self.usePrior:
         return 1.
      else:
         if i is None:
            var = self.var
         else:
            var = self.var[i]
         return exp((1./(2*(var**2))) * ((x2 ** 2).sum() - (x1 ** 2).sum()))
         

class Bernoulli(Distribution):
   def __init__(self, config):
      super(Bernoulli, self).__init__(config)
      self.dim = config.dim
      self.bitFlipProb = .5

   def __call__(self, **kwargs):
      return random.binomial(1, self.bitFlipProb, self.dim)
      
   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)] 

class BernoulliTernary(Distribution):
   def __init__(self, config):
      super(BernoulliTernary, self).__init__(config)
      self.dim = config.dim

   def __call__(self, **kwargs):
      numBytes = int(ceil(self.dim / 8.0))
      numFull  = self.dim / 8
      initial = ''
      if numBytes != numFull:
         extra = self.dim % 8
         initMask = 0
         for i in xrange(extra):
            initMask <<= 1
            initMask |= 1
         initial = struct.pack('B',initMask)
            
      base = long(binascii.hexlify(random.bytes(numBytes)), 16)
      known = long(binascii.hexlify(initial + '\xff'*numFull), 16)
      return TernaryString(base, known)
      
   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)] 


class LogNormalRing(ProposalDistribution):
   def __init__(self, config):
      super(LogNormalRing, self).__init__(config)
      self.dim = 2
      self.bounded = config.bounded
      self.var = 1.
      self.varIncr = 1.1
      self._mean = -10.
      
   def __call__(self, **kwargs):
      magnitude = random.lognormal(self.mean(), self.variance())
      angle = random.random_sample() * 2 * pi
      
      x = cos(angle) * magnitude
      y = sin(angle) * magnitude
      
      varied = array([x,y])
      
      # check bounds; call again if outside bounds
      if self.bounded:
         pass
      
      return varied

   def mean(self):
      return self._mean
   
   def variance(self):
      return 1.
            
   def adjust(self, rate):
      pass

   def densityRatio(self, x1, x2):
      r1 = sqrt((x1 ** 2).sum())
      r2 = sqrt((x2 ** 2).sum())
      num = r1 * exp(-((log(r2) - self.mean()) **2)/ 2 / (self.variance() ** 2))
      denom = r2 * exp(-((log(r1) - self.mean()) ** 2) / 2 / (self.variance() ** 2))
      return num / denom

class FixedCube(ProposalDistribution):
   def __init__(self, config):
      super(FixedCube, self).__init__(config)
      self.scale = config.scale
      self.dim = config.dim
      self.center = config.center
      
   def __call__(self, **kwargs):
      return (random.random_sample(self.dim) - .5) * 2 * self.scale + self.center

   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)] 

   def densityRatio(self, x1, x2):
      return 1.

   def adjust(self, rate):
      pass



