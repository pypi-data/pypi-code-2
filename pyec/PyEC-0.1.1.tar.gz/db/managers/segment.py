from numpy import *
from django.db import models

class SegmentManager(models.Manager):
   """ 
      Provides several segment level operations
      
      Call as Segment.objects.foo(), not SegmentManager().foo()
   """

   def clearSegment(self, segment):
      """ Clear all database objects associated with the segment """
      from django.db import connection, transaction
      cursor = connection.cursor()
      cursor.execute("DELETE FROM db_scoretree WHERE segment_id=%s", [segment.id])
      cursor.execute("DELETE FROM db_partition WHERE segment_id=%s", [segment.id])
      cursor.execute("DELETE FROM db_point WHERE segment_id=%s", [segment.id])
      transaction.commit_unless_managed()


   def updateProbs(self, mult, diff, div, segment):
      """
         Update probabilities for all points in the segment using counts
         WARNING: This requires linear time and is not recommended for use.
         
         Not supported outside of postgres.
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_prob_index(%s, %s, %s, %s)'
      cursor.execute(sql, [mult, diff, div, segment.id])
      transaction.commit_unless_managed()
   
   def updateProbsPartition(self, mult, diff, div, segment):
      """
         Update probabilities for all points in the segment using the partition tree.
         WARNING: This requires linear time and is not recommended for use.
         
         Not supported outside of postgres.
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_prob_index_partition(%s, %s, %s, %s)'
      cursor.execute(sql, [mult, diff, div, segment.id])
      transaction.commit_unless_managed()
   
   def updateProbsSharpen(self, multIncr, segment):
      """
         Update probabilities for all points in the segment, without exponentiation
         WARNING: This requires linear time and is not recommended for use.
         
         Not supported outside of postgres.
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_prob_index_sharpen(%s,%s)'
      cursor.execute(sql, [multIncr, segment.id])
      transaction.commit_unless_managed()   
            
   def updateProbsRaw(self, segment):
      """
         Update probabilities for all points in the segment, without exponentiation or annealed temperature
         WARNING: This requires linear time and is not recommended for use.
         
         Not supported outside of postgres.
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_prob_index_normal(%s)'
      cursor.execute(sql, [segment.id])
      transaction.commit_unless_managed()

   def updateDistances(self, segment):
      """
         Update the point-to-point distances table.
         
         Not currently used (N^2 complexity)
      
         Not supported outside of postgres
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_distances(%s)'
      cursor.execute(sql, [segment.id])
      transaction.commit_unless_managed()

   def updateCounts(self, segment, variance):
      """
         Update the counts within the database using the distance table.
         
         Not currently used.
         
         Not supported outside of postgres.
      """
      from django.db import connection, transaction
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      
      sql = 'SELECT update_counts(%s, %s)'
      cursor.execute(sql, [segment.id, variance])
      transaction.commit_unless_managed()
   
   def buildCubeCheck(self, dim, width, field='point', pfxCenter='gp.', pfxOuter='gp2.'):
      """
         Build a query to locate all points within a hypercube around a center point.
         
         If array indices are indexed (e.g. in postgres), then this requires logarithmic time per point. 
         Elsewhere it will be linear per point.
         
         dim - the dimension of the points to compare
         width - half the side length of the bounding hypercube
         field - the array on the center point to check, default "point"
         pfxCenter - a database alias (with trailing period) for the table where the center is drawn
         pfxOuter - a database alias (with trailing period) for the table where the comparison points are drawn
      """
      base = '${outer}point[%s] >= ${center}${field}[%s] - %s AND ${outer}point[%s] <= ${center}${field}[%s] + %s'
      
      radiusCmpList = []
      params = []
      for i in xrange(dim):
          idx = i+1
          radiusCmpList.append(base)
          params.extend([idx, idx, width, idx, idx, width])
      radiusCmp = ' AND '.join(radiusCmpList)
      return Template(radiusCmp).substitute(outer=pfxOuter, center=pfxCenter, field=field), params
   
   def updateCountsFromCube(self, dim, segment, stddev):
      """
         Update counts for each point in the segment with the number of other points contained in a hypercube
         for which the sides are one standard deviation away from the center on each axis.
         
         A hypercube is used because it is easier to compute than a hypersphere in Euclidean space.
         
         WARNING: This function is N log N on backends that can index points, and N^2 if the points are not indexed.
         
         Not currently used - the point indices are too expensive to build and maintain.
         
         
         dim - the dimension of the points
         segment - the segment to update
         stddev - the area within which to count
      """
      from django.db import connection, transaction
      cursor = connection.cursor()
      
      radiusCmp, params = self.buildCubeCheck(dim, stddev)
      
      sql = Template('''
         UPDATE db_point as gp 
         SET count= (
            SELECT count(*) FROM db_point as gp2
            WHERE gp2.segment_id=gp.segment_id AND gp2.alive AND
                  $radiusCmpStr
         )   
         WHERE gp.alive AND gp.segment_id=%s
            ''').substitute(radiusCmpStr=radiusCmp) 
      params.append(segment.id)
      #print sql, params
      cursor.execute(sql, params)
      transaction.commit_unless_managed()   
            
   def pruneNew(self, dim, segment, clearance):
      """
         Deactivate points within a hypercube whose sides are a distance of "clearance" from the center, ordered by score.
         
      """
      from django.db import connection, transaction
      cursor = connection.cursor()
    
      radiusCmp, params = self.buildCubeCheck(dim, clearance, '$1', '', 'gp.')
      ps = [str(p) for p in params]
      distClause = radiusCmp % tuple(ps)
      sql = "SELECT prune_new(%s, %s)"
      cursor.execute(sql, [segment.id, distClause])
      transaction.commit_unless_managed()
      
   def getAvgMax(self, segment, popSize):
      """
         Get a list of the average and maximum scores for a segment where all points are stored in the database.
         
         segment - the segment to check
         popSize - the size of the population for each generation
      """
      sql = """
         select 
            1 + floor(t.num/%s) as epoch, avg(t.score), max(t.score)
         from       
         (select (row_number() over (order by id)) as num, score 
          from db_point where segment_id=%s order by id) as t
         group by epoch order by epoch
            """
      sql = """
         select 
            1 + (t.id/%s) as epoch, avg(t.score), max(t.score)
         from       
         (select id, score 
          from db_point where segment_id=%s order by id) as t
         group by epoch order by epoch
            """
      
      from django.db import connection, transaction
      cursor = connection.cursor()   
      cursor.execute(sql, [popSize, segment.id])
      return cursor.fetchall()