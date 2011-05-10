from pyec.distribution.convolution import Convolution
from pyec.distribution import Gaussian as SimpleGaussian
from pyec.distribution import BernoulliTernary as SimpleBernoulli
from pyec.distribution import FixedCube
from mutators import *
from selectors import *
from pyec.distribution.bayes.mutators import *
from pyec.distribution.bayes.sample import DAGSampler
from pyec.config import Config, ConfigBuilder

import logging
log = logging.getLogger(__file__)  
      
class SimpleExtension(PopulationDistribution):
   def __init__(self, toExtend, extension):
      self.toExtend = toExtend
      self.extension = extension
      self.config = self.toExtend.config
    
   def __call__(self):
      return append(self.toExtend.__call__(), self.extension, axis=0)

   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)]

   def update(self, generation, population):
      self.toExtend.update(generation, population)

class ESConfigurator(ConfigBuilder):
   registryKeys = ('varInit', 'center', 'scale', 'mu', 'rho', 'mutation', 'crossover', 'selection', 'cmaCumulation', 'cmaCorrelation', 'cmaDamping')
   registry = {
      'sphere': (1.0, 0, 5.12, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'ellipsoid': (0.05, 0, 5.12, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'rotatedEllipsoid': (0.05, 0, 5.12, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'rosenbrock': (0.5, 0, 5.12, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'rastrigin': (0.05, 0, 5.12, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'miscaledRastrigin': (0.05, 0, 5.12, 10, 2, "cma", "none", "plus", .025, .025, .00005),
      'schwefel': (5.0, 0, 512, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'salomon': (0.5, 0, 30, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'whitley': (1.0, 0, 5.12, 10, 1, "cma", "dominant", "plus", .025, .025, .00005),
      'ackley': (1.0, 0, 30, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'langerman': (0.5, 0, 15, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'shekelsFoxholes': (1.0, 0, 15, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'shekel2': (1.0, 5, 10, 10, 1, "cma", "none", "plus", .025, .025, .00005),
      'rana': (5.0, 0, 520, 10, 1, "cma", "none", "plus", .025, .025, .00005 ),
      'griewank': (30, 0, 600, 10, 1, "cma", "none", "plus", .025, .025, .00005 ),
   }

   def __init__(self, *args):
      super(ESConfigurator, self).__init__(EvolutionStrategy)
      self.cfg.crossover = "dominant"
      self.cfg.selection = "plus"
      self.cfg.mu = 10
      self.cfg.lmbda = 50
      self.cfg.rho = 1
      self.cfg.space = "real"
      self.cfg.mutation = "cma"
      self.cfg.cmaCumulation = .025
      self.cfg.cmaCorrelation = .025
      self.cfg.cmaDamping = .00005
      
class EvolutionStrategy(Convolution):
   unsorted = False
   def __init__(self, config):
      """ 
         Config options:
             mu - number of parents
             rho - number of parents for crossover
             selection - (plus, comma)
             crossover - (dominant, intermediate)

      """
      self.config = config
      self.selectors = []
      self.selectors.append(EvolutionStrategySelection(config))
      self.selector = Convolution(self.selectors)
      self.mutators = []
      if config.rho > 1:
         if config.crossover == 'dominant':
            crosser = DominantCrosser()
         elif config.crossover == 'intermediate':
            crosser = IntermediateCrosser()
         else:
            raise Exception, "Unknown crossover method"
         order = config.rho
         self.mutators.append(Crossover(self.selector, crosser, order))
      if config.space == 'real':
         if hasattr(config, 'mutation') and config.mutation == 'cma':
            self.mutators.append(CorrelatedEndogeneousGaussian(config))
            if config.bounded:
               initial = SimpleExtension(FixedCube(config), self.buildRotation(config))
            else:
               initial = SimpleExtension(SimpleGaussian(config), self.buildRotation(config))
         else:
            self.mutators.append(EndogeneousGaussian(config))
            if config.bounded:
               initial = SimpleExtension(FixedCube(config), ones(config.dim))
            else:
               initial = SimpleExtension(SimpleGaussian(config), ones(config.dim))
      elif config.space == 'binary':
         bitFlip = 0.05
         if hasattr(config, 'bitFlipProbs'):
            bitFlip = config.bitFlipProbs
         self.mutators.append(Bernoulli(bitFlip))
         initial = SimpleBernoulli(config)
      else:
         raise Exception, "Unknown space"
      self.mutator = Convolution(self.mutators)
      
      super(EvolutionStrategy, self).__init__([self.selector, self.mutator], initial)
      
   def convert(self, x):
      return x[:self.config.dim]
         
   def buildRotation(self, config):
      ret = []
      for i in xrange(config.dim):
         for j in xrange(config.dim):
            if i == j:
               ret.append(config.varInit)
            elif j > i:
               ret.append(0.0)
      ret = append(array(ret), zeros(config.dim), axis=0)
      ret = append(array(ret), ones(config.dim), axis=0)
      ret = append(array(ret), zeros(config.dim), axis=0)
      return ret
      
   @classmethod
   def configurator(cls):
      return ESConfigurator(cls)

