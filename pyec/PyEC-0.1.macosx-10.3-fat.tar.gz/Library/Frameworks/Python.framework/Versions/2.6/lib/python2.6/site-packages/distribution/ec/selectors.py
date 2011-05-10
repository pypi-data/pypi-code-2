from numpy import *
import copy, traceback, sys
from pyec.distribution.basic import PopulationDistribution
from pyec.db.models import Point, Partition, ScoreTree, Segment
from pyec.util.TernaryString import TernaryString

import logging
logger = logging.getLogger(__file__)

class Selection(PopulationDistribution):
   """A selection method"""
   pass

class EvolutionStrategySelection(Selection):
   def __init__(self, config):
      super(EvolutionStrategySelection, self).__init__(config)
      self.total = 0
      self.mu = config.mu
      self.plus = config.selection == 'plus' # plus or comma selection, for ES

   def __call__(self):
      idx = random.randint(0,self.mu-1)
      return self.population[idx]

   def batch(self, popSize):
      if self.plus:
         return self.population \
          + [self.__call__() for i in xrange(popSize - self.mu)]
      else:
         return [self.__call__() for i in xrange(popSize)]

   def update(self, generation, population):
      """the population is ordered by score, take the first mu as parents"""
      self.population = [x for x,s in population][:self.mu]
      


class Proportional(Selection):
   def __init__(self, config):
      super(Proportional, self).__init__(config)
      self.total = 0
      self.matchedPopulation = []

   def __call__(self):
      rnd = random.random_sample() * self.total
      for x,amt in self.matchedPopulation:
         if amt >= rnd:
            return x
      return self.matchedPopulation[-1][0]
      

   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)]

   def update(self, generation, population):
      self.population = copy.deepcopy(population)
      self.total = sum([s for x,s in population])
      self.matchedPopulation = []
      amt = 0
      for x,s in population:
         amt += s
         self.matchedPopulation.append((x,amt))
      return self.population

   
class Tournament(Selection):
   def __init__(self, config):
      super(Tournament, self).__init__(config)
      self.pressure = config.selectionPressure
      self.total = 0
      self.matchedPopulation = []


   def __call__(self):
      rnd = random.random_sample() * self.total
      for x,amt in self.matchedPopulation:
         if amt >= rnd:
            return x
      return self.matchedPopulation[-1][0]
    

   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)]

   def update(self, generation, population):
      self.population = copy.deepcopy(population)
      self.matchedPopulation = []
      amt = self.pressure
      self.total = 0
      for x,s in population:
         self.matchedPopulation.append((x,amt))
         self.total += amt
         amt *= (1 - self.pressure)
      return self.population

class Ranker(object):
   def __call__(self, rank, popSize):
      pass

class LinearRanker(Ranker):
   def __init__(self, pressure):
      """pressure between 1.0 and 2.0"""
      self.pressure = pressure

   def __call__(self, rank, popSize):
      return 2 - self.pressure + (2 * (self.pressure-1))* ((rank-1.0)/(popSize - 1.0)) 
      
class NonlinearRanker(Ranker):
   def __init__(self, pressure, popSize):
      self.pressure = pressure
      self.coeffs = [self.pressure for i in xrange(popSize)]
      self.coeffs[0] -= popSize
      self.root = roots(self.coeffs)[0].real

   def __call__(self, rank, popSize):
      """ root is root of (pressure * sum_k=0^(popSize-1) x^k) - popSize * x ^(popSize - 1)"""
      return self.root ** (rank - 1.0) 


class Ranking(Selection):
   """Takes a ranking function which weights individuals according to rank
      Rank is 1 for lowest, K for highest in population of size K"""
   def __init__(self, config):
      super(Ranking, self).__init__(config)
      self.ranker = config.ranker
      self.total = 0
      self.matchedPopulation = []

   def __call__(self):
      rnd = random.random_sample() * self.total
      for x,amt in self.matchedPopulation:
         if amt >= rnd:
            return x
      return self.matchedPopulation[-1][0]
      

   def batch(self, popSize):
      return [self.__call__() for i in xrange(popSize)]

   def update(self, generation, population):
      self.population = copy.deepcopy(population)
      self.matchedPopulation = []
      amt = 0
      idx = len(population)
      for x,s in population:
         amt += self.ranker(idx, len(population))
         self.matchedPopulation.append((x,amt))
         idx -= 1
      self.total = amt
      return self.population

class Elitist(Selection):
   def __init__(self, config):
      super(Elitist, self).__init__(config)
      self.maxScore = -1e100
      self.maxOrg = None
      self.population = None

   def batch(self, popSize):
      return self.population

   def update(self, generation, population):
      if population[0][1] > self.maxScore or self.maxOrg is None:
         self.maxScore = population[0][1]
         self.maxOrg = population[0][0]
         self.population = copy.deepcopy(population)
      else:
         self.population = [(self.maxOrg, self.maxScore)]
         self.population.extend(population)
         self.population = self.population[:-1]


class Annealing(Selection):
   def __init__(self, config):
      super(Annealing, self).__init__(config)
      self.n = 0
      self.segment = None
      self.activeField = config.activeField
      config.taylorCenter = 1.0
      if not hasattr(config, 'taylorDepth'):
         config.taylorDepth = 0
      if not hasattr(config, 'shiftToDb'):
         config.shiftToDb = True
   
   def getArea(self, id):
      return Partition.objects.get(point__id=id).area      
                     
   def __call__(self, **kwargs):
      # handle initial case
      id = None
      if self.n == 0:
         center = self.config.initialDistribution()
      else:
         # select a mixture point
         try:
            point = self.sample()
            center = getattr(point, self.activeField)
            id = point.id
         except Exception, msg:
            traceback.print_exc(file=sys.stdout)
            center = self.config.initialDistribution()
            
      if self.config.passArea:
         area = 1.0
         if id is not None:
            area = self.getArea(id)
         return center, area
      else:
         return center
      
   def batch(self, m):
      return [self() for i in xrange(m)]
      
   def update(self, n, population):
      self.n = n
      self.temp = log(n)
      if self.segment is None:
         self.segment = Segment.objects.get(name=self.config.segment)

   def density(self, temp, score, rank, area):
      return (exp(score) ** (temp * self.config.learningRate)) * area


class ProportionalAnnealing(Annealing):
   def __init__(self, config):
      if not hasattr(config, 'taylorDepth'):
         config.taylorDepth = 10
      super(ProportionalAnnealing, self).__init__(config)
      
   def sample(self):
      return Point.objects.sampleProportional(self.segment, self.temp, self.config)
      
   def update(self, n, population):
      rerun = n == self.n
      super(ProportionalAnnealing, self).update(n, population)
      if not rerun and .5 * floor(2*self.temp) > self.config.taylorCenter:
         ScoreTree.objects.resetTaylor(self.segment, .5 * floor(2 *self.temp), self.config)
      
class TournamentAnnealing(Annealing):
   def sample(self):
      return Point.objects.sampleTournament(self.segment, self.temp, self.config)
      
   def density(self, temp, score, rank, area):
      return (((1.0 - self.config.pressure) ** rank) ** (temp * self.config.learningRate)) * area 
      
      
class ConditionalSelection(Annealing):
   def sample(self):
      key = TernaryString(0L, 0L)
      bits = 0
      return Point.objects.sampleConditional(self.segment, key, bits, self.config)
      
   def getArea(self, id):
      depth = Partition.objects.computeDepth(id)
      return .5 ** depth
      
   def update(self, n, population):
      if n != self.n:
         super(ConditionalSelection, self).update(n, population)
         if hasattr(self.config.fitness, 'train'):
            self.config.fitness.train(self)

   def completeTraining(self, model):
      # rescore points and propagate sums
      for pt in Point.objects.raw("select * from db_point where segment_id=%s and alive", [self.segment.id]):
         pt.score = model(getattr(pt, self.config.activeField))
         pt.save()
      Partition.objects.updateScoresConditional(self.segment)
    
