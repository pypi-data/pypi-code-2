from numpy import *
from math import atan2
from trainer import Config, Trainer
from distribution import Metropolis, GaussianProposal, GaussianMixture, LogNormalRing, FixedCube
from approximator import GaussianProcessBuilder

from benchmark import *


cfg = Config()
cfg.dim = 5
cfg.bounded = False
cfg.equilibrium = 100
cfg.learningRate = .1
cfg.usePrior = False
cfg.scale = 10.0




def mf(x):
   """base mean func - take (n,2) shaped array, return (n) shaped """
   ret = zeros(x.shape[0])
   for i in xrange(x.shape[0]):
      ret[i] = exp(-(x[i] ** 2).sum())
   return ret
   
def neg(f):
   def nf(x):
      return f(x)
   return nf

for bm in allBenchmarks:
   metropolis = Metropolis(cfg, 
                        GaussianProcessBuilder(mf), 
                        GaussianProposal(cfg))
   trainer = Trainer(neg(bm), metropolis, cfg)
   trainer.train()
   