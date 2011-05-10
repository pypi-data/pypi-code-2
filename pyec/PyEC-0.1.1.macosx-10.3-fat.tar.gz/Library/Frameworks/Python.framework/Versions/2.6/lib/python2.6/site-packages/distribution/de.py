from numpy import *
from basic import PopulationDistribution, FixedCube
from pyec.config import Config, ConfigBuilder

class DEConfigurator(ConfigBuilder):
   registryKeys = ('crossoverProb', 'learningRate', 'center', 'scale')
   registry = {
      'sphere': (0.1, 0.25, 0, 5.12),
      'ellipsoid': (0.1, 0.25, 0, 5.12),
      'rotatedEllipsoid': (0.1, 0.25, 0, 5.12),
      'rosenbrock': (0.9, 0.9, 0, 5.12),
      'rastrigin': (0.1, 0.25,  0, 5.12),
      'miscaledRastrigin': (0.1, 0.25, 0, 5.12),
      'schwefel': (0.1, 0.25, 0, 512),
      'salomon': (0.1, 0.25, 0, 30),
      'whitley': (0.9, 0.9, 0, 5.12),
      'ackley': (0.2, 0.5, 0, 30),
      'langerman': (0.1, 0.25, 0, 15),
      'shekelsFoxholes': (0.2, 0.9, 0, 15),
      'shekel2': (0.2, 0.9, 5, 10),
      'rana': (.2, 0.9, 0, 520),
      'griewank': (.2, 0.9, 0, 600),
      'weierstrass': (.2, 0.9, 0, 0.5)
   }

   def __init__(self, *args):
      super(DEConfigurator, self).__init__(DifferentialEvolution)
      self.cfg.sort = False
      self.cfg.crossoverProb = .5
      self.cfg.learningRate = .5
   
   def postConfigure(self, cfg):
      cfg.initialDistribution = FixedCube(cfg)

   

class DifferentialEvolution(PopulationDistribution):
   unsorted = True

   def __init__(self, cfg):
      super(DifferentialEvolution, self).__init__(cfg)
      self.CR = self.config.crossoverProb
      self.F = self.config.learningRate
      self.initial = self.config.initialDistribution
      self.xs = zip(self.initial.batch(self.config.populationSize), [None for i in xrange(self.config.populationSize)])
      

   @classmethod
   def configurator(cls):
      return DEConfigurator(cls)
      
   def batch(self, popSize):
      idx = 0
      ys = []
      for x,s in self.xs:
         y = 2 * (self.config.scale + self.config.center) * ones(self.config.dim)
         while (abs(y - self.config.center) > self.config.scale).any():
            i1 = idx
            while i1 == idx:
               i1 = random.randint(0,self.config.populationSize)
            i2 = i1
            while i1 == i2 or i2 == idx:
               i2 = random.randint(0,self.config.populationSize)
            i3 = i2
            while i1 == i3 or i2 == i3 or i3 == idx:
               i3 = random.randint(0,self.config.populationSize)
         
            a, s1 = self.xs[i1]
            b, s2 = self.xs[i2]
            c, s3 = self.xs[i3]
         
            d = random.randint(0, len(x))
            y = copy(x)
            idx2 = 0
            for yi in y:
               r = random.random_sample()
               if idx2 == d or r < self.CR:
                  y[idx2] = a[idx2] + self.F * (b[idx2] - c[idx2]) 
               idx2 += 1 
         ys.append(y)
         idx += 1
      return ys
      

   def update(self, generation, population):
      idx = 0
      # print [s for x,s in self.xs][:5]
      for y,s2 in population:
         x,s = self.xs[idx]
         if s is None or s2 >= s:
            self.xs[idx] = y,s2 
         idx += 1
         
