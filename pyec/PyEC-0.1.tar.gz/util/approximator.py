from pymc.gp import *
from numpy import *
from math import atan2

class GaussianProcess:
   def __init__(self, mean, covar):
      self.mean = mean
      self.covar = covar
      self.f = Realization(self.mean, self.covar)

   def __call__(self, x):
      
      #print x, self.f([x])[0], fitness(x)
      return self.f([x])[0]
      

class GaussianProcessBuilder:
   def __init__(self, meanFunc):
      self.meanFunc = meanFunc


   def __call__(self, points, targets):
      if not len(points):
         return lambda x: exp(-(x**2).sum())
      points = array(points)
      targets = array(targets)
      
      mean = Mean(self.meanFunc)
      covar = Covariance(eval_fun = matern.euclidean, 
                         diff_degree = 0.5, 
                         amp = .4, 
                         scale = 1., 
                         rank_limit=100000)
      observe(M=mean, 
              C=covar, 
              obs_mesh=points, 
              obs_V=0.001, 
              obs_vals = targets,
              cross_validate=False)
      
      return GaussianProcess(mean, covar)