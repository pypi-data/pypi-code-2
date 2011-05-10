from numpy import *
from django.db import models
from pyec.constants import *

class PointManager(models.Manager):
   """
      Provides sampling methods for evolutionary annealing.
      
      Call as Point.objects.sample(segment), not as PointManager().sample(segment).
   """
   def sample(self, segment):
      """
         Sample from the probIndex probability vector on Point.
      
         Only supported for Postgres
      
         segment - the Segment object from which to sample.
      """
      from django.db import connection
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      
      return self.raw('SELECT * from db_point where id = (select grid_point_sample(%s))', [segment.id])[0]
   
   def sampleTournamentInDb(self, segment, temp, config):
      """
         Like sampleTournament, but in PL/PGSQL.
         
         Only supported in Postgres.
      
         segment - the segment to sample 
         temp - the temperature at which to sample
         config - a evo.config.Config object containing parameters "pressure" and "learningRate"
      """
      from django.db import connection
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      ret = self.raw('SELECT * from db_point where id = (select sample_tournament(%s,%s, %s,%s))', [segment.id, config.pressure, config.learningRate, float(temp)])[0]
      return ret
   
   def sampleTournament(self, segment, temp, config):
      """
         Sample evolutionary annealing in tournament mode by walking the (balanced) score tree
      
         segment - the segment to sample 
         temp - the temperature at which to sample
         config - a evo.config.Config object containing parameters "pressure" and "learningRate"
         
         if config.shiftToDb is True, this will attempt to call sampleTournamentInDb.
      """
      if config.shiftToDb:
         try:
            from pyec.db.models import UnsupportedBackendException
            return self.sampleTournamentInDb(segment, temp, config)
         except UnsupportedBackendException, msg:
            config.shiftToDb = False
      from pyec.db.models import ScoreTree
      current = ScoreTree.objects.raw("""select * from db_scoretree where parent_id is null and segment_id=%s""", [segment.id])[0]
      while True:
         children = list(ScoreTree.objects.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [current.id]))
      
         if len(children) == 0:
            break
         
         try:
            p = 1. / (1. + ((1. - config.pressure) ** (config.learningRate * temp * (2 ** children[0].height))))
         except:
            p = 1.0
         
         if p < 1.0:
            p = (p / (1. - p))
            p *= children[0].area;
            p /= p + children[1].area;
         
         if random.random_sample() < p:
            current = children[0]
         else:
            current = children[1]
         
      return self.raw("""select * from db_point where id=%s""", [current.point_id])[0]
            
   def sampleProportional(self, segment, temp, config):
      """
         Sample evolutionary annealing in proportional mode by walking the (balanced) score tree.
      
         segment - the segment to sample 
         temp - the temperature at which to sample
         config - a evo.config.Config object containing parameters "pressure" and "learningRate"
         
         if config.shiftToDb is True, this will attempt to use a stored procedure for postgres.
      """
      # choose the proper center
      # this function has better approximates to the right of the center
      center = config.taylorCenter
      offset = 0
      depth = config.taylorDepth
      if config.shiftToDb:
         from django.db import connection
         if connection.settings_dict['ENGINE'] == POSTGRES_BACKEND:
            ret = self.raw('SELECT * from db_point where id = (select sample_taylor(%s,%s,%s,%s,%s))', [segment.id, depth, offset, center, float(temp)])[0]
            return ret
      
      from pyec.db.models import ScoreTree
      current = ScoreTree.objects.raw("""select * from db_scoretree where parent_id is null and segment_id=%s""", [segment.id])[0]
      children = list(ScoreTree.objects.raw("""select * from db_scoretree where parent_id=%s""", [current.id]))
      ns = array([i+0. for i in xrange(depth)])
      diffs = (temp - center) ** ns
      while len(children) > 0:
         # build choice
         p1 = (children[0].taylor[offset:offset+depth] * diffs).sum()
         p2 = (children[1].taylor[offset:offset+depth] * diffs).sum()
         if p1 > 0.0 or p2 > 0.0:
            p1 = p1 / (p1 + p2)
         else:
            p1 = .5
         idx = 1
         if random.random_sample() < p1:
            idx = 0
         current = children[idx]
         children = list(ScoreTree.objects.raw("""select * from db_scoretree where parent_id=%s""", [current.id]))
      
      
      return self.raw("""select * from db_point where id=%s""", [current.point_id])[0]
      
   def sampleConditional(self, segment, key, bits, config):
      from django.db import connection
      cursor = connection.cursor()
      
      sql = """
         SELECT id, score_sum, "index" FROM db_partition 
         WHERE parent_id=(
            SELECT id FROM db_partition 
            WHERE parent_id IS NULL and segment_id=%s
         )
         ORDER BY upper
      """
      cursor.execute(sql, [segment.id])
      scores = list([(int(x[0]), float(x[1]), int(x[2])) for x in cursor.fetchall()])
      
      
      while len(scores) > 0:
         if scores[0][2] < bits:
            # forced choice
            # check the indexed bit, go to the higher upper if true
            if key[scores[0][2]]:
               parentId = scores[1][0]
            else:
               parentId = scores[0][0]
         else:
            # random choice
            p = scores[0][1] / (scores[0][1] + scores[1][1])
            if random.random_sample() < p:
               parentId = scores[0][0]
            else:
               parentId = scores[1][0]
         
         sql = """
            SELECT id, score_sum, "index" FROM db_partition WHERE parent_id=%s
            ORDER BY upper
         """
         cursor.execute(sql, [parentId])
         scores = list([(int(x[0]), float(x[1]), int(x[2])) for x in cursor.fetchall()])
         
      return self.raw("""select * from db_point where id=(select point_id from db_partition where id=%s)""", [parentId])[0]

