#import psyco
#psyco.full()


from numpy import *
from evo.trainer import Config, Trainer
from evo.distribution.basic import Gaussian, FixedCube
from evo.distribution.sa import *

from evo.util.benchmark import *

import sys
if len(sys.argv) > 1:
   name = sys.argv[1]
else:
   name = "all"
if len(sys.argv) > 2:
   index = sys.argv[2]
else:
   index = None

cfg = Config()
cfg.dim = 5
cfg.bounded = True
cfg.equilibrium = 100
cfg.learningRate = 1.0
cfg.usePrior = False
cfg.scale = 10.0
cfg.populationSize = 1
cfg.generations = 25000

cfg.usePrior=True
cfg.varInit=1
cfg.divisor = 100.




   
def neg(f):
   def nf(x):
      return -f(x)
   return nf

variance = {
   'sphere': (0.05, .01, 0, 5.12),
   'ellipsoid': (0.05, 5.12),
   'rotatedEllipsoid': (0.05, 0, 5.12),
   'rosenbrock': (0.05, 1.0, 0.01, 0, 5.12),
   'rastrigin': (0.05, 0, 5.12),
   'miscaledRastrigin': (0.05, 0, 5.12),
   'schwefel': (5.0, 0, 512),
   'salomon': (0.5, 0, 30),
   'whitley': (0.05, .1, .01, 0, 5.12),
   'ackley': (0.5, 1.0, .01, 0, 30),
   'langerman': (0.5, 0, 15),
   'shekelsFoxholes': (1.0, 0.2, .01, 0, 15),
   'shekel2': (1.0, 0.2, .01, 5, 10),
   'rana': (5.0, 0, 520)
}

estimates = 1

for bm in allBenchmarks:
   if name != "all" and bm.name != name:
      continue
   if hasattr(bm, 'constraints'):
      cfg.bounded = True
      cfg.scale = bm.constraints[1]
   cfg.varInit, cfg.learningRate, cfg.restartProb, cfg.center, cfg.scale = variance[bm.name] 
   cfg.initial = FixedCube(cfg)
   fitnesses = []
   points = []
   for i in xrange(estimates):
      if index is None:
         idx = i
      else:
         idx = index
      cfg.segment = 'sa.' + bm.name + '.' + str(idx)
      cfg.proposal = Gaussian(cfg)
      pso = SimulatedAnnealing(cfg)
      trainer = Trainer(neg(bm), pso, cfg)
      fitness, point = trainer.train()
      print i, bm.name, '\t\t\t', fitness, '\t', point
      fitnesses.append(fitness)
      points.append(point)
   print "averages:\t", sum(fitnesses)/estimates, array(points).sum(axis=0)/estimates
   
