from numpy import *
import gc, traceback, sys
from time import time
from django import db
import logging
log = logging.getLogger(__file__)

from pyec.util.TernaryString import TernaryString
from pyec.db.models import Segment, Point, Partition, ScoreTree

class BadAlgorithm(Exception):
   pass
   
class RunStats(object):
   totals = {}
   times = {}
   counts = {}
   recording = True
   
   def start(self, key):
      if not self.recording: return
      if not self.totals.has_key(key):
         self.totals[key] = 0.0
         self.counts[key] = 0
      self.times[key] = time()

   def stop(self, key):
      if not self.recording: return
      now = time()
      self.totals[key] += now - self.times[key]
      del self.times[key]
      self.counts[key] += 1
      
   def __getitem__(self, key):
      return self.totals[key] / self.counts[key]
      
   def __str__(self):
      ret = ""
      for key,val in sorted(self.totals.items(), key=lambda x: x[0]):
         ret += "%s: %.9f\n" % (key, self[key])
      return ret

class Trainer(object):
   def __init__(self, fitness, evoAlg, **kwargs):
      self.fitness = fitness
      self.algorithm = evoAlg
      self.config = evoAlg.config
      self.sort = True
      self.segment = None
      self.start = 0
      config = self.config
      try:
         self.segment = Segment.objects.get(name=config.segment)
         if hasattr(config, 'preserve') and config.preserve:
            # level to population size and update
            numPoints = len(Point.objects.filter(segment=self.segment))
            numGens = int(floor(numPoints / config.populationSize))
            for point in Point.objects.filter(segment=self.segment)[(numGens * config.populationSize):]:
               point.delete()
            if numGens > 0:
               population = [(gp.point, gp.score) for gp in Point.objects.filter(segment=self.segment)[(numGens - 1)*config.populationSize:]]
               self.algorithm.update(numGens + 1, population) 
               self.start = numGens
         else:
            Segment.objects.clearSegment(self.segment)
            self.segment.delete()
            self.segment = None
      except Exception, msg:
         print Exception, msg
         self.segment = None
      partition = None
      if self.segment is None:
         print "creating segment"
         self.segment = Segment(name=config.segment, config=config)
         partition = Partition(
            segment = self.segment,
            index = 0,
            parent = None,
            upper = config.center + config.scale,
            lower = config.center - config.scale,
            area = 1.0,
            point = None
         )
         scoreRoot = ScoreTree(
            segment = self.segment,
            parent = None,
            point = None
         )
         self.segment.save()
      if partition is not None:
         partition.segment = self.segment
         partition.save()
         scoreRoot.segment = self.segment
         scoreRoot.save()
      if hasattr(config, 'sort'):
         self.sort = config.sort



   def train(self):
      stats = RunStats()
      stats.recording = self.config.recording
      maxScore = -1e100
      maxOrg = None
      if self.start > 0:
         gp = Point.objects.filter(segment=self.segment).order_by('-score')[0]
         maxScore = gp.score
         maxOrg = gp.point
      gens = self.config.generations - self.start
      if gens < 1:
         return maxScore, maxOrg
      for idx in xrange(gens):
         startTime = time()
         stats.start("generation")
         i = idx + self.start
         population = []
         start = time()
         stats.start("sample")
         for x in self.algorithm.batch(self.config.populationSize):
            stats.stop("sample")
            stats.start("score")
            if not hasattr(self.config, 'convert') or self.config.convert:
               score = self.fitness(self.algorithm.convert(x))
            else:
               score = self.fitness(x)
            stats.stop("score")
            population.append((x,score))
            stats.start("sample")
         if self.sort:
            population = sorted(population, key=lambda x: x[1], reverse=True)   
            genmax = population[0][1]
            genorg = population[0][0]
         else:
            genmax = max([s for x,s in population])
            for x,s in population:
               if s == genmax:
                  genorg = x
                  break
         
         if genmax > maxScore:
            del maxOrg
            del maxScore
            maxScore = genmax
            maxOrg = genorg
            if not isinstance(maxOrg, ndarray) and not isinstance(maxOrg, TernaryString):
               maxOrg.computeEdgeStatistics()
               print maxOrg.edges
         else:
            del genorg
         for point, score in population:
            try:
               pt = None
               bn = None
               bit = None
               if isinstance(point, ndarray):
                  pt = maximum(1e-30 * ones(len(point)), abs(point))
                  pt *= sign(point)
                  #rad = sqrt(((pt - identity(self.config.dim, float)) ** 2).sum(axis=1))
               elif isinstance(point, TernaryString):
                  bit = point
               else:
                  bn = point
                  # bn.computeEdgeStatistics()
                  # print bn.edges
               gp = Point(point=pt, bayes=bn, binary=bit, score=score, count=1, segment=self.segment)
               gp.save()
               if hasattr(self.config, 'partition') \
                and self.config.partition:
                  try:
                     stats.start("separate")
                     Partition.objects.separate(gp, self.config, stats)
                     stats.stop("separate")
                     stats.start("insert")
                     ScoreTree.objects.insert(gp, self.config, stats)
                     stats.stop("insert")
                  except:
                     #log.exception("Exception when partitioning")
                     gp.alive = False
                     gp.save()
               del gp
            except:
               raise #Exception, str(point)
         stats.start("update")
         self.algorithm.update(i+2,population)
         stats.stop("update")
         stats.stop("generation")
         if self.config.recording:
            print stats
         del population
         db.reset_queries()
         gc.collect()
         if hasattr(self.algorithm, 'var'):
            print i, ": ", time() - startTime, self.algorithm.var, '%.16f' % genmax, '%.16f' % maxScore   
         else:
            print i, ": ", time() - startTime, genmax, maxScore
      return maxScore, maxOrg
