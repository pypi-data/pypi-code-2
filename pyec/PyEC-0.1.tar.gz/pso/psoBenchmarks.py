#import psyco
#psyco.full()


from numpy import *
from evo.trainer import Config, Trainer
from evo.distribution.pso import *

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
cfg.populationSize = 100
cfg.generations = 500

cfg.omega = 1.0
cfg.phip = 0.25
cfg.phig = 0.25




   
def neg(f):
   def nf(x):
      return -f(x)
   return nf

variance = {
   'sphere': (0.05, 1.0, 0.0625, 0, 5.12, 1.0),
   'ellipsoid': (0.05, 0.0625, 1.0, 0, 5.12, 1.0),
   'rotatedEllipsoid': (0.05, 0.0625, 1.0, 0, 5.12, 1.0),
   'rosenbrock': (0.05, 1.0, 0.0625, 0, 5.12, 1.0),
   'rastrigin': (0.05, 0.0625, 1.0,  0, 5.12, 1.0),
   'miscaledRastrigin': (0.05, 0.0625, 1.0, 0, 5.12, 1.0),
   'schwefel': (5.0, 1.0, 0.25, 0, 512, 1.0),
   'salomon': (0.5, 1.0, 0.0625, 0, 30, 1.0),
   'whitley': (0.05, 1.0, 0.0625, 0, 5.12, 1.0),
   'ackley': (0.5, 1.0, 0.0625, 0, 30, 1.0),
   'langerman': (0.5, 1.0, 0.00625, 0, 15, 1.0),
   'shekelsFoxholes': (5.0, 1.0, 0.00625, 0, 15, 1.0),
   'shekel2': (5.0, 1.0, 0.00625, 5, 10, 1.0),
   'rana': (5.0, 1.0, 0.00625, 0, 520, 1.0)
}

estimates = 1

for bm in allBenchmarks:
   if name != "all" and bm.name != name:
      continue
   if hasattr(bm, 'constraints'):
      cfg.bounded = True
      cfg.scale = bm.constraints[1]
   cfg.segment = 'benchmark.' + bm.name
   cfg.varInit, cfg.varDecay, cfg.varExp, cfg.center, cfg.scale, cfg.learningRate = variance[bm.name] 
   fitnesses = []
   points = []
   for i in xrange(estimates):
      if index is None:
         idx = i
      else:
         idx = index
      cfg.segment = 'pso.' + bm.name + '.' + str(idx)
      pso = ParticleSwarmOptimization(cfg)
      trainer = Trainer(neg(bm), pso, cfg)
      fitness, point = trainer.train()
      print i, bm.name, '\t\t\t', fitness, '\t', point
      fitnesses.append(fitness)
      points.append(point)
   print "averages:\t", sum(fitnesses)/estimates, array(points).sum(axis=0)/estimates
   
