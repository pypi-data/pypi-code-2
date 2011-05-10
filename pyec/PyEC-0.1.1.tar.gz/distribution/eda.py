from numpy import *
import numpy.linalg

from pyec.distribution.basic import *
from pyec.distribution.bayes.net import BayesNet
from pyec.distribution.bayes.sample import DAGSampler
from pyec.distribution.bayes.structure.greedy import GreedyStructureSearch
from pyec.distribution.bayes.score import BayesianDirichletScorer, BayesianInformationCriterion
from pyec.distribution.bayes.variables import *
from pyec.util.TernaryString import TernaryString

from pyec.config import ConfigBuilder

seterr(divide="ignore")

class RBoaConfigurator(ConfigBuilder):
   registryKeys = ('center','scale')
   registry = {
      'sphere': (0, 5.12),
      'ellipsoid': (0, 5.12),
      'rotatedEllipsoid': (0, 5.12),
      'rosenbrock': (0, 5.12),
      'rastrigin': (0, 5.12),
      'miscaledRastrigin': (0, 5.12),
      'schwefel': (0, 512),
      'salomon': (0, 30),
      'whitley': (0, 5.12),
      'ackley': (0, 30),
      'langerman': (0, 15),
      'shekelsFoxholes': (0, 15),
      'shekel2': (5, 10),
      'rana': (0, 520),
      'griewank': (0,600),
      'weierstrass':(0,0.5),
   }
   
   def __init__(self, *args):
      super(RBoaConfigurator, self).__init__(Boa)
      self.cfg.toSelect = 20
      self.cfg.space = 'real'
      self.cfg.branchFactor = 3

class BoaConfigurator(RBoaConfigurator):
   def __init__(self, *args):
      super(BoaConfigurator, self).__init__(*args)
      self.cfg.space = 'binary'
      self.cfg.branchFactor = 10
      self.cfg.binaryDepth = 16

   def postConfigure(self, cfg):
      cfg.rawdim = cfg.dim
      cfg.rawscale = cfg.scale
      cfg.rawcenter = cfg.center
      cfg.dim = cfg.dim * cfg.binaryDepth
      cfg.center = .5
      cfg.scale = .5 

class Boa(PopulationDistribution):
   unsorted = False

   def __init__(self, cfg):
      super(Boa, self).__init__(cfg)
      self.dim = cfg.dim
      self.selected = cfg.toSelect
      if cfg.space == 'real':
         cfg.variableGenerator = lambda i: GaussianVariable(i, cfg.dim, cfg.scale)
         cfg.structureGenerator = GreedyStructureSearch(cfg.branchFactor, BayesianInformationCriterion())
         cfg.randomizer = lambda x: zeros(cfg.dim)
         cfg.sampler = DAGSampler()
         self.network = BayesNet(cfg)
         self.initial = FixedCube(cfg)
      else:
         cfg.variableGenerator = BinaryVariable
         cfg.structureGenerator = GreedyStructureSearch(cfg.branchFactor, BayesianDirichletScorer())
         cfg.randomizer = lambda x: TernaryString(0L,0L)
         cfg.sampler = DAGSampler()
         self.network = BayesNet(cfg)
         self.initial = BernoulliTernary(cfg)
      self.trained = False
      self.cfg = cfg
      self.elitist = False
      if hasattr(cfg, 'elitist') and cfg.elitist:   
         self.elitist = True
      self.maxScore = 0
      self.maxOrg = None

   def __call__(self):
      if not self.trained:
         return self.initial.__call__()
      x = self.network.__call__()
      if self.cfg.space == "binary":
         x = self.decodeData(x)
      elif self.cfg.bounded and (abs(x - self.cfg.center) > self.cfg.scale).any():
         return self.__call__()
      #print x   
      return x

   def batch(self, num):
      return [self.__call__() for i in xrange(num)]

   def update(self, generation, population):
      self.trained = True
      if self.maxOrg is None or self.maxScore <= population[0][1]:
         self.maxOrg = population[0][0]
         self.maxScore = population[0][1]
      if self.elitist:
         data = [self.convertData(self.maxOrg), self.maxScore] + [self.convertData(x) for x,s in population[:self.selected]]
      else:
         data = [self.convertData(x) for x,s in population[:self.selected]]
      self.network.structureSearch(data)
      self.network.update(generation, data)
   
   def convert(self, x):
      if self.config.space == "binary":
         ns = array([i+1 for i in xrange(self.config.binaryDepth)] * self.config.rawdim)
         ms = .5 ** ns
         y = reshape(x * ms, (self.config.binaryDepth, self.config.rawdim))
         y = y.sum(axis=0).reshape(self.config.rawdim)
         return y * self.config.rawscale + self.config.rawcenter
      return x
   
   def convertData(self, x):
      return x
   
   def decodeData(self, x):
      return y
   
   @classmethod
   def configurator(cls):
      return BoaConfigurator(cls)   
            
class hBoa(object):
   def batch(self, popSize):
      pass

   def update(self, generation, population):
      pass
