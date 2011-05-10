import sys, traceback

from django.conf import settings
from numpy import *
from pyec.db.models import Point, Segment, ScoreTree
from pyec.config import Config, ConfigBuilder
from basic import PopulationDistribution, FixedCube

class MixtureConfigurator(ConfigBuilder):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (5.0, 0.5, 0.5, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (8.0, 2.5, 0.25, 0, 5.12, 2.5),
      'rastrigin': (1.0, 1.0, 0.2, 0, 5.12, .1),
      'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (16.0, 1.0, 0.25, 0, 512, .001),
      'salomon': (3.0, 1.0, 0.0625, 0, 30, 1.0),
      'whitley': (8.0, 0.5, 0.33333333, 0, 5.12, 0.1),
      'ackley': (32.0, 1.0, 0.25, 0, 30, 1.0),
      'langerman': (8.0, 2.5, 0.25, 5, 10, 10.0),
      'shekelsFoxholes': (16.0, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (32.0, 1.0, 0.25, 5, 10, 0.5),
      'rana': (64.0, 1.0, 0.25, 0, 520, 1.0),
      'griewank': (256.0, 0.25, 0.25, 0.0, 600, 10.0),
   }
   
   def __init__(self):
      super(MixtureConfigurator, self).__init__(GaussianMixture)
      self.cfg.oscillation = False
      self.cfg.partition = True
      self.cfg.shiftToDb = True
      self.cfg.taylorDepth = 10
      self.cfg.selection = "proportional"
      self.cfg.varInit = 1.0
      self.cfg.varDecay = 2.5
      self.cfg.varExp = 0.25
      self.cfg.learningRate = 1.0
      self.cfg.refinePoint = 1e100
      self.cfg.pressure = 0.025
      
   def setTournament(self, pressure=0.025):
      self.cfg.selection = "rank"
      self.cfg.taylorDepth = 0
      self.cfg.pressure = pressure
      
   def setProportional(self, taylorDepth=100):
      self.cfg.taylorDepth = taylorDepth
      self.cfg.selection = "proportional"

   def postConfigure(self, cfg):
      cfg.initialDistribution = FixedCube(cfg)

class MixtureTournamentConfigurator(MixtureConfigurator):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (5.0, 0.5, 0.75, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (8.0, 2.5, 0.33, 0, 5.12, 5.0),
      'rastrigin': (8.0, 1.0, 0.25, 0, 5.12, 1.0),
      'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (16.0, 1.0, 0.25, 0, 512, .001),
      'salomon': (3.0, 1.0, 0.0625, 0, 30, 1.0),
      'whitley': (8.0, 1.0, 0.33333333, 0, 5.12, 0.25),
      'ackley': (32.0, 2.5, 0.25, 0, 30, 1.0),
      'langerman': (8.0, 2.5, 0.25, 5, 10, 10.0),
      'shekelsFoxholes': (16.0, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (32.0, 0.5, 0.3333333, 5, 10, 0.5),
      'rana': (64.0, 1.0, 0.25, 0, 520, 1.0),
      'griewank': (256.0, 1.0, 0.333333333, 0.0, 600, 10.0),
   }
   def __init__(self):
      super(MixtureTournamentConfigurator,self).__init__()
      self.setTournament()

class BayesMixtureConfigurator(ConfigBuilder):
   def __init__(self):
      super(BayesMixtureConfigurator, self).__init__(BayesMixture)
      self.cfg.center = .5
      self.cfg.scale = .5
      self.cfg.dim = cfg.numVariables ** 2
      self.cfg.varDecay = 1.0
      self.cfg.varExp = 0.25
      self.cfg.bounded = False
      self.cfg.initialDistribution = None
      self.cfg.data = None
      self.cfg.randomizer = None
      self.cfg.variableGenerator = None
      self.cfg.mergeProb = 0
      self.cfg.partition = True
      self.cfg.shiftToDb = True
      self.cfg.taylorDepth = 10
      self.cfg.selection = "proportional"

class Mixture(PopulationDistribution):
   def __init__(self, config):
      super(PopulationDistribution, self).__init__(config)
      self.mixturePoints = []
      self.mixtureWeights = [] # should sum to 1
      self.mixtureWeightsRaw = []
      self.counts = [] # count number of points within one s.d.
      self.dim = config.dim
      self.bounded = config.bounded
      self.learningRate = config.learningRate
      self.config = config
      self.var = config.varInit
      self.n = 0
      self.segment = None
      self.oscillate = True
      if hasattr(config, 'oscillation') and not config.oscillation:
         self.oscillate = False
      self.partition = False
      if hasattr(config, 'partition'):
         self.partition = config.partition
      self.activeField = 'point'
      self.refinePoint = 1L << 1000
      if hasattr(config, 'refinePoint'):
         self.refinePoint = config.refinePoint
      self.config.refining = False
      config.lastTemp = 1.0
      self.proportional = True
      if hasattr(config, 'selection') and config.selection == "rank":
         self.proportional = False
      config.taylorCenter = 1.0
      if not hasattr(config, 'taylorDepth'):
         if self.proportional:
            config.taylorDepth = 100
         else:
            config.taylorDepth = 1
      if not hasattr(config, 'selectionPressure'):
         config.selectionPressure = 2.0
      if not hasattr(config, 'shiftToDb'):
         config.shiftToDb = True
   
   @classmethod
   def configure(cls):
      return MixtureConfigurator(cls)
   
   def __call__(self, **kwargs):
      # handle initial case
      count = 1
      if self.n == 0:
         if hasattr(self.config, 'initialDistribution'):
            center = self.config.initialDistribution()
         else:
            center = zeros(self.dim)
      else:
         # select a mixture point
         try:
            if self.partition:
               if self.proportional:
                  point = Point.objects.sampleProportional(self.segment, self.temp, self.config)
               else:
                  point = Point.objects.sampleTournament(self.segment, self.temp, self.config)
                  #print "sample: ", 1. / (self.config.learningRate * self.temp), point.id, point.score
            else:
               point = Point.objects.sample(self.segment)
            center = getattr(point, self.activeField)
            count = point.count
         except Exception, msg:
            #traceback.print_exc(file=sys.stdout)
            if hasattr(self.config, 'initialDistribution'):
               center = self.config.initialDistribution()
            else:
               center = zeros(self.dim)
      return center, count
   
   def batch(self, m):
      for i in xrange(m):
         yield self()
      raise StopIteration
   
   def update(self, n, population):
      self.n = n
      if n > self.refinePoint and not self.config.refining:
         self.config.refining = True
         Partition.objects.resetTaylor(self.segment, self.config.taylorCenter, self.config)
      self.temp = log(n)
      self.config.lastTemp = self.temp
      if self.segment is None:
         self.segment = Segment.objects.get(name=self.config.segment)
      if self.partition and self.proportional:
         if floor(self.temp) > self.config.taylorCenter:
            ScoreTree.objects.resetTaylor(self.segment, floor(self.temp), self.config)


class GaussianMixture(Mixture):
   varIncr = 1.1

   def __call__(self, **kwargs):
      center, count = super(GaussianMixture, self).__call__(**kwargs)
      
      if self.n == 0:
         return center
      
      # vary the mixture point
      varied = random.randn(self.dim) * self.variance() + center
      
      #print center, varied, self.variance()
      
      # check bounds; call again if outside bounds
      if self.bounded:
         if (abs(varied - self.config.center) > self.config.scale).any():
            return self.__call__(**kwargs)
      
      return varied
   
   def dist(self, x1, x2):
      return sqrt(((x1 - x2) ** 2).sum())
         
   def variance(self):
      return self.var

   def adjust(self, rate):
      if rate < .23:
         self.var *= self.varIncr
      else:
         self.var /= self.varIncr

   def densityRatio(self, x1, x2):
      if len(self.mixturePoints) == 0:
         return 1.
         #return exp((1./(2*(self.variance()**2))) * ((x2 ** 2).sum() - (x1 ** 2).sum()))
      num = exp(1. / (2*(self.variance() **2)) * ((x2 - array(self.mixturePoints)) ** 2).sum(axis=1))
      denom = exp(1. / (2*(self.variance() **2)) * ((x1 - array(self.mixturePoints)) ** 2).sum(axis=1))
      num = (array(self.mixtureWeights) * num).sum()
      denom = (array(self.mixtureWeights) * denom).sum()
      # print "density: ", x1, x2, num, denom, num/denom
      return num / denom
      
   def update(self, n, population):
      super(GaussianMixture, self).update(n, population)
      self.var = self.config.varInit * exp(-(n * self.config.varDecay) ** self.config.varExp) 
      if self.oscillate:
         self.var *= exp(self.config.varAmp * sin(n))
      #print "variance:", self.var
      if not self.partition:
      #   GridSegment.objects.updateProbsPartition(float(log(n) * self.config.learningRate), 0, 1, self.segment)
      #else:
         GridSegment.objects.updateCountsFromCube(self.dim, self.segment, float(self.var))
         GridSegment.objects.updateProbs(float(log(n) * self.config.learningRate), 0, 1, self.segment)
      
      #print "variance: ", self.var, len(self.mixturePoints)

class CauchyMixture(Mixture):
   varIncr = 1.1

   def __call__(self, **kwargs):
   
      #if random.random_sample() < .05:
      #   return random.randn(self.dim) * 1.0
   
   
      center, count = super(CauchyMixture, self).__call__(**kwargs)
      
      if self.n == 0:
         return center
      
      # vary the mixture point
      varied = random.standard_cauchy(self.dim) * self.variance() + center
      
      #print center, varied, self.variance()
      
      # check bounds; call again if outside bounds
      if self.bounded:
         if (abs(varied - self.config.center) > self.config.scale).any():
            return self.__call__(**kwargs)
      
      return varied
   
   def dist(self, x1, x2):
      return sqrt(((x1 - x2) ** 2).sum())
         
   def variance(self):
      return self.var

   def adjust(self, rate):
      if rate < .23:
         self.var *= self.varIncr
      else:
         self.var /= self.varIncr

   def densityRatio(self, x1, x2):
      if len(self.mixturePoints) == 0:
         return 1.
         #return exp((1./(2*(self.variance()**2))) * ((x2 ** 2).sum() - (x1 ** 2).sum()))
      num = exp(1. / (2*(self.variance() **2)) * ((x2 - array(self.mixturePoints)) ** 2).sum(axis=1))
      denom = exp(1. / (2*(self.variance() **2)) * ((x1 - array(self.mixturePoints)) ** 2).sum(axis=1))
      num = (array(self.mixtureWeights) * num).sum()
      denom = (array(self.mixtureWeights) * denom).sum()
      # print "density: ", x1, x2, num, denom, num/denom
      return num / denom
      
   def update(self, n, population):
      super(CauchyMixture, self).update(n, population)
      self.var = self.config.varInit * exp(-(n * self.config.varDecay) ** self.config.varExp) # exp(-(len(self.mixturePoints)**.125))
      if self.oscillate:
         self.var *= exp(sin(n))
      #print "variance:", self.var
      if not self.partition:
         #GridSegment.objects.updateProbsPartition(float(log(n) * self.config.learningRate), 0, 1, self.segment)
      #else:
         GridSegment.objects.updateCountsFromCube(self.dim, self.segment, float(self.var))
         GridSegment.objects.updateProbs(float(log(n) * self.config.learningRate), 0, 1, self.segment)
      
      #print "variance: ", self.var, len(self.mixturePoints)


class BernoulliMixture(Mixture):

   def __call__(self, **kwargs):
      center, count = super(BernoulliMixture, self).__call__(**kwargs)
      
      # vary the mixture point
      varied = abs(center - random.binomial(1, self.bitFlipProb(), self.dim))
      
      # check bounds
      if self.bounded:
         pass 
         
      return varied

   def bitFlipProb(self):
      return 1. / len(self.mixturePoints)

class BayesMixture(Mixture):
   def __init__(self, config):
      super(BayesMixture, self).__init__(config)
      self.activeField = 'bayes'

   def __call__(self, **kwargs):
      center, count = super(BayesMixture, self).__call__(**kwargs)
      
      # print "center: ", center.edges
      
      if self.n == 0:
         return center
         
         
      if random.random_sample() < self.config.mergeProb:
         center2, count = super(BayesMixture, self).__call__(**kwargs)
         center.merge(center2, self.config.data)
      
      # vary the mixture point
      center.decay = self.decay
      #center.computeEdgeStatistics()
      #print center.edges
      center.structureGenerator.config = self.config
      varied = center.structureSearch(self.config.data)
      
      # print "varied: ", varied.edges
      
      return varied

   def update(self, n, population):
      super(BayesMixture, self).update(n, population)
      # GridSegment.objects.updateProbsPartition(float(log(n) * self.config.learningRate), 0, 1, self.segment)
      
      self.decay = (self.n * self.config.varDecay) ** self.config.varExp
      self.decay *= exp(sin(n))
      
   @classmethod   
   def configurator(cls, numVariables=0):
      return BayesMixtureConfigurator(cls, numVariables)

      
