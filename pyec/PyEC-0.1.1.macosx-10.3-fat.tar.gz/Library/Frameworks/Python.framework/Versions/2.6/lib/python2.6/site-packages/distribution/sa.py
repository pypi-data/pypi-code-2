from numpy import *
from basic import PopulationDistribution, Gaussian, FixedCube

from pyec.config import ConfigBuilder

class SAConfigurator(ConfigBuilder):
   registryKeys = ('varInit','learningRate','restartProb','center','scale')
   registry = {
      'sphere': (0.5, 10.0, 0.001, 0, 5.12),
      'ellipsoid': (0.05, 1.0, 0.001, 0.0, 5.12),
      'rotatedEllipsoid': (0.05, 1.0, 0.001, 0, 5.12),
      'rosenbrock': (0.5, 1.0, 0.001, 0, 5.12),
      'rastrigin': (0.5, 0.1, 0.001, 0, 5.12),
      'miscaledRastrigin': (0.05, 1.0, 0.001, 0, 5.12),
      'schwefel': (50.0, 0.01, 0.001, 0, 512),
      'salomon': (5.0, .1, 0.001, 0, 30),
      'whitley': (5.0, .1, .001, 0, 5.12),
      'ackley': (5.0, .25, .001, 0, 30),
      'langerman': (1.0, 5.0, 0.001, 5, 10),
      'shekelsFoxholes': (1.0, 0.25, 0.001, .01, 0, 15),
      'shekel2': (5.0, 0.25, .001, 5, 10),
      'rana': (50.0, 1.0, 0.001, 0, 520),
      'griewank': (50.0, 10.0, 0.001, 0, 600),
      'weierstrass': (0.1, 5.0, 0.001, 0.0, 0.5),
   }
   
   def __init__(self, *args):
      super(SAConfigurator, self).__init__(SimulatedAnnealing)
      self.cfg.usePrior = True
      self.cfg.divisor = 100.0
      
   def postConfigure(self, cfg):
      cfg.initial = FixedCube(cfg)
      cfg.proposal = Gaussian(cfg)

# now define general sampler
class SimulatedAnnealing(PopulationDistribution):
   def __init__(self, config):
      super(SimulatedAnnealing, self).__init__(self)
      self.dim = config.dim
      self.proposal = config.proposal
      self.initial = config.initial
      self.config = config
      self.points = None
      self.accepted = 0
      self.learningRate = config.learningRate
      self.total = 0
      self.offset = 0
      self.n = 1
      config.sort = False
      self.best = None
      self.bestScore = None
      self.bestVar = self.config.varInit
      
   @classmethod
   def configurator(cls):
      return SAConfigurator(cls)   
      
   def proposalInner(self, **kwargs):
      x = self.proposal(**kwargs)
      if self.config.bounded:
         while (abs(x - self.config.center) > self.config.scale).any():
            x = self.proposal(**kwargs)
      return x
      
   def batch(self, howMany):
      if self.points is None:
         return [self.initial() for i in xrange(howMany)]
      return [self.proposalInner(prior=self.points[i][0], idx=i) for i in xrange(howMany)]


   @property
   def var(self):
      if hasattr(self.proposal, 'var'):
         if hasattr(self.proposal.var, '__len__'):
            return self.proposal.var.sum() / len(self.proposal.var)
         return self.proposal.var
      elif hasattr(self.proposal, 'bitFlipProbs'):
         return self.proposal.bitFlipProbs
      
   def temperature(self):
      return self.learningRate * (((self.n - self.offset)/self.config.divisor))

   def update(self, n, population):
      self.n = n
      if self.points is None:
         self.accepted = zeros(len(population))
         self.total = ones(len(population))
         self.points = [(x,s) for x,s in population]
         return
      #print "generation ", n, ":", [s for x,s in self.points]
      #print self.proposal.var
      
      if self.best is None: 
         self.best = [None for i in xrange(len(population))]
         self.bestScore = [None for i in xrange(len(population))]
         self.bestVar = self.bestVar * ones(len(population))
      for i in xrange(len(population)):
         if self.best[i] is None or self.bestScore[i] < population[i][1]:
            self.best[i] = population[i][0]
            self.bestScore[i] = population[i][1]
            if hasattr(self.proposal, 'var'):
               self.bestVar[i] = self.proposal.var
         self.total[i] += 1
         if self.points[i][1] < population[i][1]:
            #print "accepted better", i, self.points[i][1], population[i][1]
            self.points[i] = population[i]
            self.accepted[i] += 1
         else:
            temp = self.temperature()
            ratio = exp(-(self.points[i][1] - population[i][1])/temp)
            ratio *= self.proposal.densityRatio(self.points[i][0], population[i][0], i)
            #print ratio
            test = random.random_sample()
            if test <= ratio:
               self.accepted[i] += 1
               #print "accepted worse", i, self.points[i][1], population[i][1]
               self.points[i] = population[i]
                 
      #print self.accepted / self.total
      if n % 25 == 0:
         self.proposal.adjust(self.accepted / self.total)
         self.accepted = zeros(len(population))
         self.total = zeros(len(population))
      
      #randomly restart
      if random.random_sample() < self.config.restartProb:
         self.points = [(self.best[i], self.bestScore[i]) for i in xrange(len(population))]
         self.offset = n - 1 
         #if hasattr(self.proposal, 'var'):
         #   self.proposal.var = self.bestVar
      
         
      
      
