from numpy import *
from basic import Distribution

# now define general sampler
class Metropolis(Distribution):
   def __init__(self, config, approximator, proposal):
      super(Distribution, self).__init__(config)
      self.dim = config.dim
      self.bounded = config.bounded
      self.approximator = approximator
      self.approximation = lambda x: exp(-(x**2).sum())
      self.proposal = proposal
      self.config = config
      self.points = []
      self.targets = []
      self.accepted = 0
      self.total = 0
      self.n = 1
      
   def __call__(self, **kwargs):
      x1 = self.proposal()
      a1 = self.approximation(x1)
      f1 = exp(self.n*self.config.learningRate*a1)
      for i in xrange(self.config.equilibrium):
         x2 = self.proposal(prior=x1)
         a2 = self.approximation(x2)
         f2 = exp(self.n*self.config.learningRate*a2)
         ratio = f2 / f1 * self.proposal.densityRatio(x1,x2)
         test = random.random_sample()
         if test >= ratio:
            self.accepted += 1
            x1 = x2
            f1 = f2
            a1 = a2
         self.total += 1
      #print "sample: ", x1, " - ", f1, " - ", a1
      return x1

   def batch(self, howMany):
      acc = 0
      toBurn = self.config.equilibrium
      if self.n == 1: 
         toBurn = 0
      x1 = self.proposal()
      # print "start at: ", x1
      a1 = self.approximation(x1)
      f1 = exp(log(self.n)*self.config.learningRate*a1)
      while acc < howMany:
         x2 = self.proposal(prior=x1)
         a2 = self.approximation(x2)
         f2 = exp(log(self.n)*self.config.learningRate*a2)
         ratio = f2 / f1 * self.proposal.densityRatio(x1, x2)
         # print x1, x2, ratio, a1, a2, f1, f2
         # this assumes self.proposal is symmetric (a Gaussian is)
         # otherwise we need q12/q21
         if toBurn: toBurn -= 1
         self.total += 1
         test = random.random_sample()
         if test <= ratio:
            self.accepted += 1
            #print "accepted: ", x2, f2, a2
            x1 = x2
            f1 = f2
            a1 = a2
            if not toBurn:
               acc += 1
               # print "yielding: ", x1, " - ", ratio, " ; ", a1, " vs ", fitness(x1)
               yield x1
            if self.n > 1:
               self.proposal.adjust(float(self.accepted) / float(self.total))
      raise StopIteration
      

   def update(self, n, population):
      self.points.extend([x[0] for x in population])
      self.targets.extend([x[1] for x in population])
      self.approximation = self.approximator(self.points,self.targets)
      self.n = n
      # print "acceptance rate: ", self.accepted / (self.total + 0.)
      self.proposal.adjust(float(self.accepted) / float(self.total))
      self.proposal.update(n, population)
      self.accepted = 0
      self.total = 0
