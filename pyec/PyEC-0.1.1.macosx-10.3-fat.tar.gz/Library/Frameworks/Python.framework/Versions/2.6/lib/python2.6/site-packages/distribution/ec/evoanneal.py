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

class REAConfigurator(ConfigBuilder):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (1.0, 0.5, 0.5, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (1.0, 2.5, 0.25, 0, 5.12, 1.0),
      'rastrigin': (1.0, 1.0, 0.2, 0, 5.12, 0.1),
      'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (1.0, 1.0, 0.25, 0, 512, .015),
      'salomon': (1.0, 1.0, 0.0625, 0, 30, 2.0),
      'whitley': (1.0, 1.0, 0.33333333, 0, 5.12, 0.1),
      'ackley': (1.0, 1.0, 0.25, 0, 30, 0.25),
      'langerman': (1.0, 2.5, 0.25, 5, 10, 5.0),
      'shekelsFoxholes': (1.0, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (1.0, 1.0, 0.25, 5, 10, .25), #.25 in 5d
      'rana': (1.0, 1.0, 0.25, 0, 520, 0.0025),
      'griewank': (1.0, 0.25, 0.25, 0.0, 600, 10.0),
      'weierstrass': (1.0, 1.0, 0.25, 0.0, 0.5, 5.0)
   }
   
   def __init__(self):
      super(REAConfigurator, self).__init__(EvolutionaryAnnealing)
      self.cfg.shiftToDb = True
      self.cfg.taylorDepth = 10
      self.cfg.selection = "proportional"
      self.cfg.varInit = 1.0
      self.cfg.varDecay = 2.5
      self.cfg.varExp = 0.25
      self.cfg.learningRate = 1.0
      self.cfg.pressure = 0.025
      self.cfg.crossover = "none"
      self.cfg.mutation = "gauss"
      self.cfg.activeField = "point"
      self.cfg.partition = True
      self.cfg.passArea = True
      
   def setTournament(self, pressure=0.025):
      self.cfg.selection = "tournament"
      self.cfg.taylorDepth = 0
      self.cfg.pressure = pressure
      
   def setProportional(self, taylorDepth=100):
      self.cfg.taylorDepth = taylorDepth
      self.cfg.selection = "proportional"
      
   def setGaussian(self):
      self.cfg.mutation = "gauss"

   def setCauchy(self):
      self.cfg.mutation = "cauchy"
      
   def setCrossover(self, enable=True):
      if enable:
         self.cfg.crossover = "uniform"
         #self.cfg.crossover = "de"
         #self.cfg.derate = .9
         #self.cfg.decrossprob = .2
      else:
         self.cfg.crossover = "none"
      
   def setCMA(self):
      self.cfg.mutation = "cma"
      self.cfg.cmaCumulation = .025
      self.cfg.cmaCorrelation = .025
      self.cfg.cmaDamping = .00005
      self.cfg.convert = True

   def setEndogeneous(self):
      self.cfg.mutation = "endogeneous"

   def postConfigure(self, cfg):
      cfg.initialDistribution = FixedCube(cfg)

class REATournamentConfigurator(REAConfigurator):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (1.0, 0.5, 0.75, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (1.0, 2.5, 0.33, 0, 5.12, 5.0),
      'rastrigin': (1.0, 1.0, 0.25, 0, 5.12, 0.035),
      'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (1.0, 1.0, 0.25, 0, 512, .001),
      'salomon': (1.0, 1.0, 0.0625, 0, 30, 2.0), 
      'whitley': (1.0, 1.0, 0.33333333, 0, 5.12, 0.25),
      'ackley': (1.0, 2.5, 0.25, 0, 30, 0.25), # .25 for 5d, 1.0 works for 10d
      'langerman': (1.0, 2.5, 0.25, 5, 10, 5.0),
      'shekelsFoxholes': (1.0, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (1.0, 1.0, 0.25, 5, 10, 0.1),
      'rana': (1.0, 1.0, 0.25, 0, 520, 1.0),
      'griewank': (1.0, 1.0, 0.333333333, 0.0, 600, .1),
      'weierstrass': (1.0, 1.0, 0.25, 0.0, 0.5, 5.0)
   }
   def __init__(self):
      super(REATournamentConfigurator,self).__init__()
      self.setTournament()

class CMAREAConfigurator(REAConfigurator):
   registryKeys = ('varInit', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (1.0, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0, 5.12, 1.0),
      'rosenbrock': (1.0, 0, 5.12, 5.0),
      'rastrigin': (1.0, 0, 5.12, 1.0),
      'miscaledRastrigin': (1.0, 0, 5.12, 1.0),
      'schwefel': (1.0, 0, 512, .001),
      'salomon': (1.0, 0, 30, 1.0),
      'whitley': (1.0, 0, 5.12, 0.25),
      'ackley': (1.0, 0, 30, 1.0),
      'langerman': (8.0, 5, 10, 10.0),
      'shekelsFoxholes': (5.0, 0, 15, 1.0),
      'shekel2': (5.0, 5, 10, 0.5),
      'rana': (30.0, 0, 520, 1.0),
      'griewank': (30.0, 0.0, 600, 10.0),
   }
   
   def __init__(self):
      super(CMAREAConfigurator, self).__init__()
      self.setTournament()
      self.setCMA()

   def setCrossover(self, enabled=False):
      self.cfg.crossover = "none"

class CrossedREAConfigurator(REAConfigurator):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (5.0, 0.5, 0.5, 0, 5.12, 10.0),
      'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (8.0, 2.5, 0.25, 0, 5.12, 2.5),
      'rastrigin': (1.0, 1.0, 0.2, 0, 5.12, .1),
      'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (256.0, 1.0, 0.25, 0, 512, .01),
      'salomon': (3.0, 1.0, 0.0625, 0, 30, 1.0),
      'whitley': (8.0, 0.5, 0.33333333, 0, 5.12, 0.1),
      'ackley': (32.0, 1.0, 0.25, 0, 30, 1.0), 
      'langerman': (8.0, 2.5, 0.25, 5, 10, 10.0),
      'shekelsFoxholes': (16.0, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (32.0, 1.0, 0.25, 5, 10, 0.5),
      'rana': (64.0, 1.0, 0.25, 0, 520, 1.0),
      'griewank': (256.0, 1.0, 0.33333, 0.0, 600, 10.0),
   }
   
   def __init__(self):
      super(CrossedREAConfigurator, self).__init__()
      self.setTournament()
      self.setCrossover()

class BEAConfigurator(REAConfigurator):
   registryKeys = ('varInit', 'varDecay', 'varExp', 'center', 'scale', 'learningRate')
   registry = {
      'sphere': (0.5, 0.5, 0.5, 0, 5.12, 1000.0),
      'ellipsoid': (0.5, 0.0625, 1.0, 0, 5.12, 1.0),
      'rotatedEllipsoid': (0.5, 0.0625, 1.0, 0, 5.12, 1.0),
      'rosenbrock': (0.5, 2.5, 0.25, 0, 5.12, 2.5),
      'rastrigin': (0.5, 1.0, 0.2, 0, 5.12, .1),
      'miscaledRastrigin': (0.5, 1.0, 0.0625, 0, 5.12, 1.0),
      'schwefel': (0.5, 1.0, 0.25, 0, 512, .01),
      'salomon': (0.5, 1.0, 0.0625, 0, 30, 1.0),
      'whitley': (0.5, 0.5, 0.33333333, 0, 5.12, 0.1),
      'ackley': (0.5, 1.0, 0.25, 0, 30, 1.0),
      'langerman': (0.5, 2.5, 0.25, 5, 10, 10.0),
      'shekelsFoxholes': (0.5, 1.0, 0.3333333333, 0, 15, 1.0),
      'shekel2': (0.5, 1.0, 0.25, 5, 10, 0.5),
      'rana': (0.5, 1.0, 0.25, 0, 520, 1.0),
      'griewank': (0.5, 1.0, 0.33333, 0.0, 600, 10.0),
   }
   
   def __init__(self):
      super(BEAConfigurator, self).__init__()
      self.setTournament()
      self.setCrossover()
      self.cfg.mutation = "bernoulli"
      self.cfg.binaryDepth=16
      self.cfg.activeField="binary"
      
   def postConfigure(self, cfg):
      cfg.rawdim = cfg.dim
      cfg.rawscale = cfg.scale
      cfg.rawcenter = cfg.center
      cfg.dim = cfg.dim * cfg.binaryDepth
      cfg.center = .5
      cfg.scale = .5 
      cfg.initialDistribution = SimpleBernoulli(cfg)

class BayesEAConfigurator(REAConfigurator):
   def __init__(self):
      super(BayesEAConfigurator, self).__init__()
      self.cfg.varDecay = 1.0
      self.cfg.varExp = 0.25
      self.cfg.bounded = False
      self.cfg.initialDistribution = None
      self.cfg.data = None
      self.cfg.randomizer = None
      self.cfg.sampler = DAGSampler()
      self.cfg.numVariables = None
      self.cfg.variableGenerator = None
      self.cfg.mergeProb = 0
      self.cfg.mutation = "structure"
      self.cfg.activeField = "bayes"

   def setCrossover(self, enable=True):
      if enable:
         self.cfg.crossover = "merge"
      else:
         self.cfg.crossover = "none"

class MixtureSamplerConfigurator(REAConfigurator):
   def __init__(self):
      super(MixtureSamplerConfigurator, self).__init__()
      self.cfg.binaryPartition = True
      self.cfg.mutation = "bernoulli"
      self.cfg.selection = "conditional"
      self.cfg.activeField = "binary"
      self.cfg.center = 0.5
      self.cfg.scale = 0.5
      self.cfg.convert = False
      self.cfg.varInit = 1.0
      self.cfg.learningRate = 1.0
      self.cfg.crossoverProb = 0.5
      self.setCrossover()
      
   def postConfigure(self, cfg):
      cfg.initialDistribution = SimpleBernoulli(cfg)
      
class EvolutionaryAnnealing(Convolution):
   def __init__(self, config):
      self.config = config
      self.binary = False
      config.stddev = config.varInit
      self.selectors = []
      if config.selection == "proportional":
         self.selectors.append(ProportionalAnnealing(config))
      elif config.selection == "tournament":
         self.selectors.append(TournamentAnnealing(config))
      elif config.selection == "conditional":
         self.selectors.append(ConditionalSelection(config))
      else:
         raise Exception, "Unknown Selection"
      
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
         elif config.crossover == 'merge':
            crosser = Merger()
         elif config.crossover == 'de':
            config.crossoverOrder = 4
            crosser = DifferentialCrosser(config.derate, config.decrossprob)
         else:
            raise Exception, "Unknown crossover method"
         order = 2
         if hasattr(config, 'crossoverOrder'):
            order = int(config.crossoverOrder)
         self.mutators.append(Crossover(self.selector, crosser, order))
      
      
      
      if hasattr(config, 'crossover') and config.crossover == 'de':
         pass
      elif config.mutation == "gauss":
         if config.passArea:
            self.mutators.append(AreaSensitiveGaussian(config))
         else:
            self.mutators.append(DecayedGaussian(config))
      elif config.mutation == "uniform":
         config.passArea = False
         self.mutators.append(UniformArea(config))
      elif config.mutation == "uniformBinary":
         self.binary = not self.config.binaryPartition
         config.passArea = True
         self.mutators.append(UniformAreaBernoulli(config))
      elif config.mutation == "cauchy":
         self.mutators.append(DecayedCauchy(config))
      elif config.mutation == "bernoulli":
         self.binary = not self.config.binaryPartition
         if config.passArea:
            self.mutators.append(AreaSensitiveBernoulli(config))
         else:
            self.mutators.append(DecayedBernoulli(config))
      elif config.mutation == "structure":
         self.mutators.append(StructureMutator(config))
      elif config.mutation == "endogeneous":
         self.mutators.append(EndogeneousGaussian(config))
         config.initialDistribution = SimpleExtension(config.initialDistribution, ones(config.dim))
      elif config.mutation == "cma":
         self.mutators.append(CorrelatedEndogeneousGaussian(config))
         config.initialDistribution = SimpleExtension(config.initialDistribution, self.buildRotation(config))
      
      self.mutator = Convolution(self.mutators)
      super(EvolutionaryAnnealing, self).__init__([self.selector, self.mutator], config.initialDistribution)
      
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
   
   def convert(self, x):
      if self.binary:
         ns = array([i+1 for i in xrange(self.config.binaryDepth)] * self.config.rawdim)
         ms = .5 ** ns
         y = reshape(x.__mult__(ms), (self.config.binaryDepth, self.config.rawdim))
         y = y.sum(axis=0).reshape(self.config.rawdim)
         return y * self.config.rawscale + self.config.rawcenter
      elif hasattr(self.config, 'convert') and self.config.convert:
         return x[:self.config.dim]
      return x
   
   @property
   def var(self):
      try:
         return self.mutators[-1].sd   
      except:
         try:
            return self.mutators[-1].bitFlipProbs
         except:
            try:
               return self.mutators[-1].decay
            except:
               return 0.0
                  
   @classmethod
   def configurator(cls):
      return REAConfigurator(cls)
      
   def density(self, xs, temp=1.0):
      ds = array([0.0 for x in xs])
      total = 0.0
      for i, p in enumerate(Point.objects.filter(alive=True).order_by('-score')):
         area = self.selectors[-1].getArea(p.id)
         score = p.score
         d1 = self.selectors[-1].density(temp, score, i, area)
         print "density at rank ", i, " bin ", p.binary, " score ", p.score, ": ", d1
         total += d1
         fld = getattr(p, self.config.activeField)
         if self.config.passArea:
            for j in xrange(len(xs)):
               d2 = self.mutators[-1].density((fld, area), xs[j])
               ds[j] += d1 * d2
         else:
            for j in xrange(len(xs)):
               ds[j] += d1 * self.mutators[-1].density(fld, xs[j])
      return ds / total
      
   def completeTraining(self, model):
      return self.selectors[-1].completeTraining(model)

         

