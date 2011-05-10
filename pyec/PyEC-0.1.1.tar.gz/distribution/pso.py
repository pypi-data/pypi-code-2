from numpy import *
from basic import PopulationDistribution, FixedCube
from pyec.config import Config, ConfigBuilder

class PSOConfigurator(ConfigBuilder):
   registryKeys = ('omega', 'phig', 'phip', 'center', 'scale')
   registry = {
      'sphere': (1.0, .25, .25, 0, 5.12),
      'ellipsoid': (1.0, .25, .25, 0, 5.12),
      'rotatedEllipsoid': (1.0, .25, .25, 0, 5.12),
      'rosenbrock': (1.0, .25, .25, 0, 5.12),
      'rastrigin': (1.0, .25, .25, 0, 5.12),
      'miscaledRastrigin': (1.0, .25, .25, 0, 5.12),
      'schwefel': (1.0, .25, .25, 0, 512),
      'salomon': (1.0, .25, .25, 0, 30),
      'whitley': (1.0, .25, .25, 0, 5.12),
      'ackley': (1.0, .25, .25, 0, 30),
      'langerman': (1.0, .25, .25, 0, 15),
      'shekelsFoxholes': (1.0, .25, .25, 0, 15),
      'shekel2': (1.0, .25, .25, 5, 10),
      'rana': (1.0, .25, .25, 0, 520),
      'griewank': (1.0, .25, .25, 0, 600)
   }

   def __init__(self, *args):
      super(PSOConfigurator, self).__init__(ParticleSwarmOptimization)
      self.cfg.sort = False
      self.cfg.omega = 1.0
      self.cfg.phig = 0.25
      self.cfg.phip = 0.25
      
   def postConfigure(self, cfg):   
      cfg.initialDistribution = FixedCube(cfg)



class ParticleSwarmOptimization(PopulationDistribution):
   unsorted = True
   
   def __init__(self, cfg):
      super(ParticleSwarmOptimization, self).__init__(cfg)
      self.initial = cfg.initialDistribution
      self.positions = array(self.initial.batch(cfg.populationSize))
      self.velocities = array(self.initial.batch(cfg.populationSize))
      self.bestLocal = copy(self.positions)
      self.bestLocalScore = zeros(cfg.populationSize)
      self.omega = cfg.omega
      self.phig = cfg.phig
      self.phip = cfg.phip
      self.bestGlobal = self.bestLocal
      self.bestGlobalScore = None
   
   @classmethod
   def configurator(cls):
      return PSOConfigurator(cls)      
      
   def updateVelocity(self):
      rp = outer(random.random_sample(self.config.populationSize), ones(self.config.dim))
      rg = outer(random.random_sample(self.config.populationSize), ones(self.config.dim))
      
      #print shape(rp), shape(self.bestLocal), shape(self.bestGlobal), shape(self.positions), shape(self.velocities)
      velocities = self.omega * self.velocities \
       + self.phip * rp * (self.bestLocal - self.positions) \
       + self.phig * rg * (self.bestGlobal - self.positions)   
      del self.velocities
      self.velocities = velocities
      del rp
      del rg
      
      
   def batch(self, popSize):
      # print sqrt((velocities ** 2).sum())
      positions = self.positions + self.velocities
      positions = maximum(positions, self.config.center-self.config.scale)
      positions = minimum(positions, self.config.center+self.config.scale)
      
      return positions

   def update(self, generation, population):
      del self.positions
      self.positions = array([x for x,s in population])

      idx = 0
      maxScore = 0
      maxOrg = None
      for x,s in population:
         if maxOrg is None or s >= maxScore:
            maxOrg = x
            maxScore = s
         if self.bestGlobalScore is None or s >= self.bestLocalScore[idx]:
            self.bestLocalScore[idx] = s
            self.bestLocal[idx] = x
         idx += 1
      if self.bestGlobalScore is None or maxScore >= self.bestGlobalScore:
         self.bestGlobalScore = maxScore
         self.bestGlobal = maxOrg
         
      self.updateVelocity()
         
