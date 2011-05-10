from numpy import *
from django.db import models
from time import time
from pyec.util.TernaryString import TernaryString


class PartitionManager(models.Manager):
   """
      Methods to operate on the partition tree for evolutionary annealing.
   """
   

   def traverseInDb(self, point, config):
      """
         Like traverse(), but calls a Postgres stored proc.
      """
      pointrep = point.separable
      from pyec.db.models import convertArray, parseArray
      sql = """select traverse(%s, %s, %s, %s, %s)"""
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()   
      cursor.execute(sql, [point.segment.id, config.dim, config.center, config.scale, convertArray(pointrep)])
      raw = cursor.fetchone()
      transaction.commit_unless_managed()
      node, upper, lower = raw[0].strip("()").split('","')
      upper = parseArray(upper)
      lower = parseArray(lower)
      node = node.strip('"').strip("'()").replace('"','').split(",")
      # node = list((val or None for val in node))
      nodeId = (node[0] and int(node[0])) or None   #id
      return self.get(id=nodeId), lower, upper

   def traverse(self, point, config):
      """
         Traverse the partition tree to find the partition within which "point" is located.
         
         point - the point for searching.
         config - an evo.config.Config object with "dim", "center", and "scale" attributes.
         
         
         Returns (partition, upper, lower)
         
         partition - the matching partition
         upper - the upper boundaries of the current partition
         lower - the lower boundaries of the current partition
      """
      pointrep = point.separable
      return self.traversePoint(point.segment.id, pointrep, config)
    
   def traversePoint(self, segmentId, pointrep, config):
      
      # get the top parent
      lower = (config.center-config.scale) * ones(config.dim)
      upper = (config.center+config.scale) * ones(config.dim)
      current = self.raw("""select * from db_partition where parent_id is null and segment_id=%s""", [segmentId])[0]
      children = list(self.raw("""select * from db_partition where parent_id=%s""", [current.id]))
      while len(children) > 0:
         #print "in traverse: ", current.id, len(children)
         for child in children:
            #print "child: ", child.id, child.upper, child.lower, point.point[child.index]
            if (pointrep[child.index] <= child.upper) and \
               (pointrep[child.index] >= child.lower):
               current = child
               children = list(self.raw("""select * from db_partition where parent_id=%s""", [current.id]))
               lower[current.index] = current.lower
               upper[current.index] = current.upper
               break
      return current, lower, upper
   
   def separate(self, point, config, stats):
      """
         Insert the point into the partition tree, separating the current partition that contains it.
         
         point - the point to insert
         config - a config object with properties "shiftToDb", "dim", "center", "scale"
         stats - an evo.trainer.RunStats object
         
         If shiftToDb is true, this will attempt to call traverseInDb()
      """
      
      if config.binaryPartition:
         return self.separateConditional(point, config, stats)
      
      from pyec.db.models import Partition, ScoreTree, SeparationException, UnsupportedBackendException
      stats.start("separate.traverse")
      lr = config.learningRate
      if config.shiftToDb:
         try:
            node, lower, upper = self.traverseInDb(point, config)
         except UnsupportedBackendException:
            config.shiftToDb = False
            node, lower, upper = self.traverse(point, config)
      else:
         node, lower, upper = self.traverse(point, config)
      stats.stop("separate.traverse")
      stats.start("separate.main")
      
      if node.point_id is None:
         node.point = point
         node.save()
         return
         
      other = node.point
      node.point = None
      # node.save()
      
      newIndex = 0
      newDiff = 0
      midPoint = 0
      upPoint = other
      downPoint = point
      pointrep = point.separable
      otherrep = other.separable
      for i in xrange(len(pointrep)):
         diff = abs(pointrep[i] - otherrep[i])
         if diff > newDiff:
            newDiff = diff
            newIndex = i
            if pointrep[i] > otherrep[i]:
               upPoint = point
               downPoint = other
               midPoint = otherrep[i] \
                + (pointrep[i] - otherrep[i])/2.
            else:
               upPoint = other
               downPoint = point
               midPoint = pointrep[i] \
                + (otherrep[i] - pointrep[i])/2.
      
      if newDiff == 0.0:
        node.point = other
        # node.save()
        raise SeparationException, "No difference in points"
      
      proportion = (midPoint - lower[newIndex]) \
       / (upper[newIndex] - lower[newIndex])
      
      upArea = float(node.area * (1.0 - proportion))
      downArea = float(node.area * proportion)
      
      """
      n1 = Partition(
         upper=upper[newIndex], 
         lower=midPoint,
         segment=node.segment,
         point=upPoint,
         area = upArea,
         index = newIndex,
         parent = node
      )
      n1.save()
      n2 = Partition(
         upper=midPoint, 
         lower=lower[newIndex],
         segment=node.segment,
         point=downPoint,
         area = downArea,
         index = newIndex,
         parent = node
      )
      n2.save()
      """
      
      from django.db import connection, transaction
      cursor = connection.cursor()  
      
      sql = """
         UPDATE db_partition SET point_id=NULL WHERE id=%s;
      """
      cursor.execute(sql, [node.id])
      
      
      sql = """
         INSERT INTO db_partition(
            upper, lower, "index", segment_id, 
            point_id, area, parent_id
         )
         VALUES
            (%s,%s,%s,%s,%s,%s,%s);
      """
      cursor.execute(sql, [float(upper[newIndex]), float(midPoint), newIndex, node.segment_id, upPoint.id, upArea, node.id])
      
      
      sql = """
         INSERT INTO db_partition(
            upper, lower, "index", segment_id, 
            point_id, area, parent_id
         )
         VALUES
            (%s,%s,%s,%s,%s,%s,%s);   
      """
      cursor.execute(sql, [float(midPoint), float(lower[newIndex]), newIndex, node.segment_id, downPoint.id, downArea, node.id])
      
      transaction.commit_unless_managed()
      
      stats.stop("separate.main")
      stats.start("separate.propagate")
      
      # correct area in score tree
      from pyec.db.models import ScoreTree
      sn = ScoreTree.objects.raw("""select * from db_scoretree where point_id=%s""", [other.id])
      try:
         sn = sn[0]
         if other == downPoint:
            sn.area = downArea
         else:
            sn.area = upArea
         sql = "UPDATE db_scoretree SET area=%s WHERE id=%s"
         cursor = connection.cursor()
         cursor.execute(sql, [float(sn.area), sn.id])
         transaction.commit_unless_managed()
         if sn.parent_id is not None:
            parent = ScoreTree.objects.raw("select * from db_scoretree where id=%s", [sn.parent_id])[0]
            ScoreTree.objects.propagateArea(sn.parent, config, 0)
      except IndexError:
         pass
      
      
      stats.stop("separate.propagate")
      

   def traverseConditional(self, point, config):
      """
         Traverse the partition tree to find the partition within which "point" is located; be sensitive to the order of variables. Any path from
         the root of the partition tree should be in increasing order
         by index; breadcrumbs must be left at gaps.
         
         Space must be binary at this time point.separable should be a
         TernaryString
         
         point - the point for searching.
         config - an evo.config.Config object with "dim", "center", and "scale" attributes.
         
         
         Returns (partition, upper, lower)
         
         partition - the matching partition
         upper - the upper boundaries of the current partition
         lower - the lower boundaries of the current partition
      """
      pointrep = point.separable
      return self.traversePointConditional(point.segment.id, pointrep, config)
    
   def traversePointConditional(self, segmentId, pointrep, config):
      
      # get the top parent
      current = self.raw("""select * from db_partition where parent_id is null and segment_id=%s""", [segmentId])[0]
      children = list(self.raw("""select * from db_partition where parent_id=%s""", [current.id]))
      index = 0
      lastIndex = -1
      nextIndex = 0
      while len(children) > 0 and index < config.dim:
         #print "in traverse: ", current.id, len(children), index
         nextIndex = children[0].index
         
         if nextIndex == index:
            # no need to split here, the index increments normally
            #found = False
            for child in children:
               #print "child: ", child.id, child.upper, child.lower, pointrep[child.index]
               if (float(pointrep[child.index]) <= child.upper) and \
                  (float(pointrep[child.index]) >= child.lower):
                  current = child
                  children = list(self.raw("""select * from db_partition where parent_id=%s""", [current.id]))
                  index = current.index + 1
                  lastIndex = current.index
                  #found = True
                  break
            #if not found:
            #   raise Exception, "no matching child"
         else:
            #print current.key
            # check the key - is the first element equal?
            if current.key[index - lastIndex - 1] == pointrep[index]:
               index += 1
            else:
               # split at index
               return current, lastIndex + 1, index, nextIndex, False
               
            
      return current, lastIndex + 1, index, nextIndex, True
      
   def separateConditional(self, point, config, stats):
      #print "enter separate conditional"
      node, index, insertPoint, nextIndex, isLeaf = self.traverseConditional(point, config)
      #print "traversed"
      if isLeaf:
         # maybe increment the index, build the key
         if node.point_id is None:
            node.point = point
            node.score_sum = point.score
            node.save()
            return
         
         other = node.point
         node.point = None
         # node.save()
      
         upPoint = other
         downPoint = point
         pointrep = point.separable
         otherrep = other.separable
         key = TernaryString(0L, 0L)
         start = index
         while index < config.dim and pointrep[index] == otherrep[index]:
            key[index - start] = pointrep[index]
            index += 1
            
            
         if index >= config.dim:
            raise SeparationException, "No difference in points"   
            
         if pointrep[index] > otherrep[index]:
            upPoint = point
            downPoint = other   
      
         # area is computed from tree depth for binary vector
         upArea = 1.0
         downArea = 1.0
         
         from pyec.db.models import BinaryField
         from django.db import connection, transaction
         cursor = connection.cursor()  
      
         sql = """
            UPDATE db_partition SET point_id=NULL, key=%s WHERE id=%s;
         """
         cursor.execute(sql, [BinaryField().get_prep_value(key), node.id])
      
      
         sql = """
            INSERT INTO db_partition(
               upper, lower, "index", segment_id, 
               point_id, area, parent_id, score_sum
            )
            VALUES
               (1.0,0.5,%s,%s,%s,1.0,%s, %s);
         """
         cursor.execute(sql, [index, node.segment_id, upPoint.id, node.id, upPoint.score])
      
      
         sql = """
            INSERT INTO db_partition(
               upper, lower, "index", segment_id, 
               point_id, area, parent_id, score_sum
            )
            VALUES
               (0.5,0.0,%s,%s,%s,1.0,%s, %s);   
         """
         cursor.execute(sql, [index, node.segment_id, downPoint.id, node.id, downPoint.score])
      
         transaction.commit_unless_managed()

      else:
         from pyec.db.models import BinaryField
      
         # split current, i.e.
         # create a new node that splits at the insertPoint
         # make a new leaf node containing the new point
         # insert the splitting node between current and its parent
         
         insert = insertPoint - index
         splitDown = node.key[insert]
         currentKey = TernaryString(0L, 0L)
         for i in xrange(nextIndex - insertPoint - 1):
            currentKey[i] = node.key[i + insert + 1]
         parentKey = TernaryString(0L, 0L)
         for i in xrange(insert):
            parentKey[i] = node.key[i]
            
                  
         from django.db import connection, transaction
         cursor = connection.cursor()  
      
         # insert the parent
         sql = """
            INSERT INTO db_partition(
               upper, lower, "index", segment_id, 
               point_id, key, area, parent_id
            )
            VALUES
               (%s,%s,%s,%s,NULL,%s, 1.0,%s);
         """
         cursor.execute(sql, [node.upper, node.lower, node.index, node.segment_id, BinaryField().get_prep_value(parentKey), node.parent_id])
         parentId = cursor.lastrowid
      
         # update the current
         sql = """
            UPDATE db_partition SET upper=%s, lower=%s, key=%s, "index"=%s, parent_id=%s WHERE id=%s;
         """
         cursor.execute(sql, [splitDown and 1.0 or 0.5, splitDown and 0.5 or 0.0, BinaryField().get_prep_value(currentKey), index, parentId, node.id])
         #print "1: ", splitDown and 1.0 or 0.5, splitDown and 0.5 or 0.0 
      
         sql = """
            INSERT INTO db_partition(
               upper, lower, "index", segment_id, 
               point_id, area, parent_id, score_sum
            )
            VALUES
               (%s,%s,%s,%s,%s,1.0,%s,%s);   
         """
         cursor.execute(sql, [splitDown and 0.5 or 1.0, not splitDown and 0.5 or 0.0, index, node.segment_id, point.id, parentId, point.score])
         #print "2: ", splitDown and 0.5 or 1.0, splitDown and 0.0 or 0.5
      
         transaction.commit_unless_managed()   

      self.propagateScoreSum(node, config)
      #print "exit separate conditional"


   def propagateScoreSum(self, node, config):
      """
         Propagate the score up the tree
         
         node - the node to start at (bottom-up traversal)
         config - an evo.config.Config
         
      """
      #print "propagate score sum"
      from django.db import connection, transaction
      cursor = connection.cursor()
      currentId = node.id
      while currentId is not None:
         currentId = int(currentId)
         sql = """
            UPDATE db_partition SET
                  score_sum=(SELECT sum(score_sum) FROM db_partition WHERE parent_id=%s)
            WHERE id=%s;
         """
         cursor.execute(sql, [currentId, currentId])
         
         sql = """
            SELECT parent_id FROM db_partition WHERE id=%s
         """
         cursor.execute(sql, [currentId])
         currentId = cursor.fetchone()[0]
      transaction.commit_unless_managed()
      #print "end propagate score sum"
      
      
   def computeDepth(self, pointId):
      """
         compute the depth of the leaf that points to the db_point with id pointId
         
      """
      from django.db import connection, transaction
      cursor = connection.cursor()
      
      depth = 0
      
      sql = """
         SELECT id FROM db_partition WHERE point_id=%s
      """
      cursor.execute(sql, [pointId])
      currentId = cursor.fetchone()[0]
      while currentId is not None:
         currentId = int(currentId)
         
         sql = """
            SELECT parent_id FROM db_partition WHERE id=%s
         """
         cursor.execute(sql, [currentId])
         currentId = cursor.fetchone()[0]
         
         if currentId is not None:
            depth += 1
      
      return depth


   def updateScoresConditional(self, segment):
      from django.db import connection, transaction
      cursor = connection.cursor()
      
      sql = """
         UPDATE db_partition SET score_sum=(
            SELECT score FROM db_point WHERE id=point_id
         )
         WHERE segment_id=%s
      """
      cursor.execute(sql, [segment.id])
      
      for i in xrange(segment.config.dim):
         idx = segment.config.dim - i - 1
         for node in self.filter(index=idx, segment=segment, point=None):
            
            sql = """
               UPDATE db_partition SET score_sum=(
                  SELECT sum(score_sum) FROM db_partition AS inner 
                  WHERE inner.parent_id=%s
               )
               WHERE id=%s
            """
            cursor.execute(sql, [node.id, node.id])
         
      transaction.commit_unless_managed()
         
