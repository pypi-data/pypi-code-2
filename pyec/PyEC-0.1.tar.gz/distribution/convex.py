from numpy import *

from basic import PopulationDistribution

class ConvexEC(PopulationDistribution):
   def __init__(self, algorithms, config):
      super(ConvexEC, self).__init__(config)
      self.cfg = config
      self.cfg.sort = False # need to be sensitive to different algorithms
      self.algs = algorithms
      self.activeIdx = random.randint(0, len(self.algs))
      self.counts = ones(len(self.algs))
      self.total = self.counts.sum()
      self.burned = 0
      self.best = None
      self.bestScore = None
      self.countDecay = self.cfg.countDecay

   def updateActive(self):
      if self.burned < self.cfg.burn:
         self.activeIdx = random.randint(0, len(self.algs))
         return
      self.total = self.counts.sum()
      rnd = random.random_sample(1) * self.total
      idx = 0
      tot = 0
      for cnt in self.counts:
         tot += cnt
         if rnd < tot:
            self.activeIdx = idx
            break
         idx += 1

   def batch(self, popSize):
      return self.algs[self.activeIdx].batch(popSize)
      
   def update(self, generation, population):
      sortPop = sorted(population, key=lambda x: x[1], reverse=True)   
      genmax = sortPop[0][1]
      genorg = sortPop[0][0]
      newBest = False
      if self.best is None or self.bestScore < genmax:
         newBest = True
         self.best = genorg
         self.bestScore = genmax
      if self.burned < self.cfg.burn:
         self.burned += 1
         if newBest:
            self.counts[self.activeIdx] *= (1./self.countDecay)**3
      else:
         # update counts
         if newBest:
            self.counts[self.activeIdx] *= (1./self.countDecay)**3
         else:
            self.counts[self.activeIdx] *= self.countDecay
            
      for alg in self.algs:
         # give a sorted population to the ones that need it
         if alg.unsorted:
            alg.update(generation, population)
         else:
            alg.update(generation, sortPop)
         
      self.updateActive()
      
      print "counts: ", self.counts, self.activeIdx
         
