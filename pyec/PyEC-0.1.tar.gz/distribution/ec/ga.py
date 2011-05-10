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

class RGAConfigurator(ConfigBuilder):
   registryKeys = ('varInit', 'center', 'scale', 'selection', 'rankingMethod', 'selectionPressure', 'crossover')
   registry = {
      'sphere': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'ellipsoid': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'rotatedEllipsoid': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'rosenbrock': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'rastrigin': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'miscaledRastrigin': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'schwefel': (5.0, 0, 512, "ranking", "linear", 1.8, "uniform"),
      'salomon': (0.5, 0, 30, "ranking", "linear", 1.8, "uniform"),
      'whitley': (0.05, 0, 5.12, "ranking", "linear", 1.8, "uniform"),
      'ackley': (0.05, 0, 30, "ranking", "linear", 1.8, "uniform"),
      'langerman': (0.05, 0, 15, "ranking", "linear", 1.8, "uniform"),
      'shekelsFoxholes': (5.0, 0, 15, "ranking", "linear", 1.8, "uniform"),
      'shekel2': (2.0, 5, 10, "ranking", "linear", 1.8, "uniform"),
      'rana': (5.0, 0, 520, "ranking", "linear", 1.8, "uniform"),
      'griewank': (10.0, 0, 600, "ranking", "linear", 1.8,"uniform"),
   }

   def __init__(self, *args):
      super(RGAConfigurator, self).__init__(GeneticAlgorithm)
      self.cfg.elitist = False
      self.cfg.selection = "ranking"
      self.cfg.rankingMethod = "linear"
      self.cfg.selectionPressure = 1.8
      self.cfg.crossover = "uniform"
      self.cfg.crossoverOrder = 2
      self.cfg.space = "real"


class GAConfigurator(RGAConfigurator):
   def __init__(self, *args):
      super(GAConfigurator, self).__init__(*args)
      self.cfg.space = "binary"
      self.cfg.activeField = "binary"
      self.cfg.binaryDepth = 16

   def postConfigure(self, cfg):
      cfg.rawdim = cfg.dim
      cfg.rawscale = cfg.scale
      cfg.rawcenter = cfg.center
      cfg.dim = cfg.dim * cfg.binaryDepth
      cfg.center = .5
      cfg.scale = .5 
      cfg.bitFlipProbs = .05


class GeneticAlgorithm(Convolution):
   unsorted = False

   def __init__(self, config):
      """ 
         Config options:
             elitist = (True, False)
             selection = (proportional, tournament, ranking)
             rankingMethod = (linear, nonlinear)
             crossover = (none, uniform, onePoint, twoPoint, intermediate)
             crossoverOrder = integer
             space = (real, binary)
             varInit = float or float array, standard deviation (for real space)
             bitFlipProbs = float or float array, mutation probability (for binary space)

      """
      self.config = config
      self.selectors = []
      if hasattr(config, 'elitist') and config.elitist:
         self.selectors.append(Elitist())
      if hasattr(config, 'selection'):
         if config.selection == 'proportional':
            self.selectors.append(Proportional())
         elif config.selection == 'tournament':
            self.selectors.append(Tournament(config))
         elif config.selection == 'ranking':
            if hasattr(config, 'rankingMethod') and config.rankingMethod == 'nonlinear':
               config.ranker = NonlinearRanker(config.selectionPressure, config.populationSize)
            else:
               config.ranker = LinearRanker(config.selectionPressure)
            self.selectors.append(Ranking(config))
         else:
            raise Exception, "Unknown selection method"
      else:
         self.selectors.append(Proportional(config))
      self.selector = Convolution(self.selectors)
      self.mutators = []
      if hasattr(config, 'crossover') and config.crossover != "none":
         if config.crossover == 'uniform':
            crosser = UniformCrosser()
         elif config.crossover == 'onePoint':
            crosser = OnePointCrosser()
         elif config.crossover == 'twoPoint':
            crosser = TwoPointCrosser()
         elif config.crossover == 'intermediate':
            crosser = IntermediateCrosser()
         else:
            raise Exception, "Unknown crossover method"
         order = 2
         if hasattr(config, 'crossoverOrder'):
            order = int(config.crossoverOrder)
         self.mutators.append(Crossover(self.selector, crosser, order))
      if config.space == 'real':
         variance = 1.0
         if hasattr(config, 'varInit'):
            variance = config.varInit
         config.stddev = variance
         self.mutators.append(Gaussian(config))
         if config.bounded:
            initial = FixedCube(config)
         else:
            initial = SimpleGaussian(config)
      elif config.space == 'binary':
         self.mutators.append(Bernoulli(config))
         initial = SimpleBernoulli(config)
      else:
         raise Exception, "Unknown space"
      self.mutator = Convolution(self.mutators)
      
      super(GeneticAlgorithm, self).__init__([self.selector, self.mutator], initial)
   
   def convert(self, x):
      if self.config.space == "binary":
         ns = array([i+1 for i in xrange(self.config.binaryDepth)] * self.config.rawdim)
         ms = .5 ** ns
         y = reshape(x * ms, (self.config.binaryDepth, self.config.rawdim))
         y = y.sum(axis=0).reshape(self.config.rawdim)
         return y * self.config.rawscale + self.config.rawcenter
      return x
   
   @classmethod
   def configurator(cls):
      return GAConfigurator(cls)      
