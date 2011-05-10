#import psyco
#psyco.full()


from numpy import *
from math import atan2
from evo.trainer import Config, Trainer
from evo.distribution import Gaussian, LogNormalRing, FixedCube
from evo.distribution.mixture import GaussianMixture
from evo.util.approximator import GaussianProcessBuilder

from evo.util.benchmark import *


cfg = Config()
cfg.dim = 5
cfg.bounded = True
cfg.equilibrium = 100
cfg.learningRate = 1.0
cfg.usePrior = False
cfg.scale = 10.0
cfg.populationSize = 100
cfg.generations = 1000
cfg.preserve = False
cfg.partition = True
cfg.oscillation = False

# center needs to be closer together if widely varying scores are to be compared; 5-10 is a good range for the gaps, depending...
cfg.shiftToDb = True 
cfg.selection = "rank"
cfg.pressure = .025


import sys
if len(sys.argv) > 1:
   name = sys.argv[1]
else:
   name = "all"
if len(sys.argv) > 2:
   index = sys.argv[2]
else:
   index = None
   
def neg(f):
   def nf(x):
      return -f(x)
   return nf

variance = {
   'sphere': (5.0, 0.5, 0.5, 0, 5.12, 10.0),
   'ellipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
   'rotatedEllipsoid': (1.0, 0.0625, 1.0, 0, 5.12, 1.0),
   'rosenbrock': (8.0, 2.5, 0.25, 0, 5.12, 2.5),
   'rastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
   'miscaledRastrigin': (1.0, 1.0, 0.0625, 0, 5.12, 1.0),
   'schwefel': (16.0, 1.0, 0.25, 0, 512, .001),
   'salomon': (3.0, 1.0, 0.0625, 0, 30, 1.0),
   'whitley': (8.0, 1.0, 0.333333, 0, 5.12, 2.5),
   'ackley': (32.0, 2.5, 0.25, 0, 30, 1.0),
   'langerman': (3.0, 1.0, 0.0625, 0, 15, 1000000000.0),
   'shekelsFoxholes': (16.0, 1.0, 0.3333333333, 0, 15, 1.0),
   'shekel2': (16.0, 2.5, 0.25, 5, 10, 0.5),
   'rana': (64.0, 1.0, 0.25, 0, 520, 1.0),
   'griewank': (256.0, 1.0, 0.333333333, 0.0, 600, 10.0),
}

estimates = 1

for bm in allBenchmarks:
   if name != "all" and bm.name != name:
      continue
   if hasattr(bm, 'constraints'):
      cfg.bounded = True
      cfg.scale = bm.constraints[1]
      
   
   cfg.varInit, cfg.varDecay, cfg.varExp, cfg.center, cfg.scale, cfg.learningRate = variance[bm.name] 
   cfg.initialDistribution = FixedCube(cfg)
   print variance[bm.name]
   fitnesses = []
   points = []
   for i in xrange(estimates):
      if index is None:
         idx = i
      else:
         idx = index
      cfg.segment = 'part.' + bm.name + '.' + str(idx)
      mixture = GaussianMixture(cfg)
      trainer = Trainer(neg(bm), mixture, cfg)
      fitness, point = trainer.train()
      print i, bm.name, '\t\t\t', fitness, '\t', point
      fitnesses.append(fitness)
      points.append(point)
   print "averages:\t", sum(fitnesses)/estimates, array(points).sum(axis=0)/estimates
   
