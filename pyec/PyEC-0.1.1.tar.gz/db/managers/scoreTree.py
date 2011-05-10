from numpy import *
from django.db import models
from time import time

import logging
log = logging.getLogger(__file__)

class ScoreTreeManager(models.Manager):
   def printTree(self, segment, node=None, indent=''):
      """
         Recursively print the score tree.
         
         segment - the segment for the tree to print
         node - the node to start at, or None for the root
         indent - a prefix for printing; tabs added for each new level
      """
      if node is None: 
         node = self.get(segment=segment, parent=None)
      
      print indent, node.id, ',', node.balance
      
      children = self.filter(parent=node).order_by('-min_score')
      if len(children) > 0:
         left = children[0]
         right = children[1]
         self.printTree(segment, left, indent + '\t')
         self.printTree(segment, right, indent + '\t')

   def computeHeight(self, node):
      """
         Compute the height of the tree starting at node.
         
         node - the node in the tree to start at
         
         Only in Postgres.
      """
      sql = """select compute_height(%s)"""
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()   
      cursor.execute(sql, [node.id])
      ret = int(cursor.fetchone()[0])
      transaction.commit_unless_managed()
      return ret

   def rotateLeft(self, node, config):
      """
         Perform a left rotation at a node in the tree. For balancing.
         
         node - the node to rotate left.
         config - a config object with property "shiftToDb"
         
         Returns -1, the change in tree height. This return will only be correct
         if used in the context of an AVL tree balancing algorithm - otherwise
         the height change would need to be computed differently (it is possible).
      """
      from pyec.db.models import UnsupportedBackendException
      if config.shiftToDb:
         try:
            return self.rotateLeftInDb(node, config)
         except UnsupportedBackendException:
            config.shiftToDb = False
      center = self.raw("""select * from db_scoretree where id=%s""", [node.id])[0]
      children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [center.id]))
      left = children[0]
      right = children[1]
      children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [right.id]))
      rightleft = children[0]
      rightright = children[1]   
      
      rightleft.parent = center
      right.parent = center.parent
      center.parent = right

      center.area = left.area + rightleft.area
      right.area = center.area + rightright.area
      
      center.taylor = left.taylor + rightleft.taylor
      right.taylor = center.taylor + rightright.taylor
   
      center.min_score = rightleft.min_score
      center.max_score = left.max_score
      right.min_score = rightright.min_score
      right.max_score = center.max_score
      
      center.height = max([left.height, rightleft.height]) + 1
      right.height = max([center.height, rightright.height]) + 1

      center.child_count = left.child_count + rightleft.child_count + 1
      right.child_count = center.child_count + rightright.child_count + 1

      center.balance = center.balance + 1
      if right.balance < 0:
         center.balance = center.balance - right.balance
      
      right.balance = right.balance + 1
      if center.balance > 0:
         right.balance = right.balance + center.balance
        
      
      from pyec.db.models import convertArray
      from django.db import connection, transaction
      cursor = connection.cursor()
      
      sql = """
         UPDATE db_scoretree SET parent_id=%s WHERE id=%s;
      """
      cursor.execute(sql, [rightleft.parent_id, rightleft.id])
      
      sql = """
         UPDATE db_scoretree SET parent_id=%s, area=%s, taylor=%s, min_score=%s, max_score=%s, height=%s, child_count=%s, balance=%s WHERE id=%s;
      """
      
      cursor.execute(sql, [center.parent_id, center.area, convertArray(center.taylor), center.min_score, center.max_score, center.height, center.child_count, center.balance, center.id])
      
      sql = """   
         UPDATE db_scoretree SET parent_id=%s, area=%s, taylor=%s, min_score=%s, max_score=%s, height=%s, child_count=%s, balance=%s WHERE id=%s;
      """
      
      cursor.execute(sql, [right.parent_id, right.area, convertArray(right.taylor), right.min_score, right.max_score, right.height, right.child_count, right.balance, right.id])
      transaction.commit_unless_managed()   
           
      #right.save()
      #center.save()
      #rightleft.save()
      return -1
   
            
                  
   def rotateLeftInDb(self, node, config):
      """
         Like rotateLeft(), but using a postgres stored procedure
      """
      sql = """select score_rotate_left(%s,%s, false, %s)"""
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()   
      cursor.execute(sql, [node.segment.id, node.id, config.taylorDepth])
      ret = int(cursor.fetchone()[0])
      transaction.commit_unless_managed()
      #print "rotating ", node.id, " left", ret
      return -1

   def rotateRight(self, node, config):
      """
         Perform a right rotation at a node in the tree. For balancing.
         
         node - the node to rotate right.
         config - a config object with property "shiftToDb"
         
         Returns -1, the change in tree height. This return will only be correct
         if used in the context of an AVL tree balancing algorithm - otherwise
         the height change would need to be computed differently (it is possible).
      """
      from pyec.db.models import UnsupportedBackendException
      if config.shiftToDb:
         try:
            return self.rotateRightInDb(node, config)
         except UnsupportedBackendException:
            config.shiftToDb = False
      center = self.raw("""select * from db_scoretree where id=%s""", [node.id])[0]
      children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [center.id]))
      left = children[0]
      right = children[1]
      children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [left.id]))
      leftleft = children[0]
      leftright = children[1]

      leftright.parent = center
      left.parent = center.parent
      center.parent = left

      center.area = right.area + leftright.area
      left.area = center.area + leftleft.area
      
      center.taylor = right.taylor + leftright.taylor
      left.taylor = center.taylor + leftleft.taylor
   
      center.min_score = right.min_score
      center.max_score = leftright.max_score
      left.min_score = center.min_score
      left.max_score = leftleft.max_score

      center.height = max([right.height, leftright.height]) + 1
      left.height = max([center.height, leftleft.height]) + 1

      center.child_count = leftright.child_count + right.child_count + 1
      left.child_count = center.child_count + leftleft.child_count + 1

      center.balance = center.balance - 1
      if left.balance > 0:
         center.balance = center.balance - left.balance

      left.balance = left.balance - 1
      if center.balance < 0:
         left.balance = left.balance + center.balance

      from pyec.db.models import convertArray
      from django.db import connection, transaction
      cursor = connection.cursor()

      sql = """
         UPDATE db_scoretree SET parent_id=%s WHERE id=%s;
      """
      cursor.execute(sql, [leftright.parent_id, leftright.id])
      
      sql = """
         UPDATE db_scoretree SET parent_id=%s, area=%s, taylor=%s, min_score=%s, max_score=%s, height=%s, child_count=%s, balance=%s WHERE id=%s;
      """
      cursor.execute(sql, [center.parent_id, center.area, convertArray(center.taylor), center.min_score, center.max_score, center.height, center.child_count, center.balance, center.id])
      
      sql = """
         UPDATE db_scoretree SET parent_id=%s, area=%s, taylor=%s, min_score=%s, max_score=%s, height=%s, child_count=%s, balance=%s WHERE id=%s;
      """
      
      cursor.execute(sql, [left.parent_id, left.area, convertArray(left.taylor), left.min_score, left.max_score, left.height, left.child_count, left.balance, left.id])
      transaction.commit_unless_managed()
      
      #center.save()
      #left.save()
      #leftright.save()
      return -1
      

   def rotateRightInDb(self, node):
      """
         Like rotateRight(), but using a postgres stored procedure
      """
      sql = """select score_rotate_right(%s,%s, false, %s)"""
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()   
      cursor.execute(sql, [node.segment.id, node.id, config.taylorDepth])
      ret = int(cursor.fetchone()[0])
      transaction.commit_unless_managed()
      return -1

   def traverseInDb(self, point):
      """
         Like traverse(), but uses a stored procedure in postgres.
      """
      from django.db import connection
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      sql = """select * from db_scoretree WHERE id=(select traverse_score_tree(%s, %s))"""
      return self.raw(sql, [point.segment.id, float(point.score)])[0]
   
   def traverse(self, point, config):
      """
         Traverse the score tree.
         
         point - the point to compare
         config - an evo.config.Config instance with property "shiftToDb"
         
         Returns node in the tree that must be split to insert the new point into the tree.
      """
      from pyec.db.models import UnsupportedBackendException
      if config.shiftToDb:
         try:
            return self.traverseInDb(point)
         except UnsupportedBackendException:
            config.shiftToDb = False
      current = self.raw("""select * from db_scoretree where segment_id=%s and parent_id is null""", [point.segment_id])[0]
      while True:
         children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [current.id]))
         if len(children) == 0:
            break
         if children[1].max_score < point.score:
            current = children[0]
         else:
            current = children[1]
      return current
            
   def propagateAreaInDb(self, node, config, inserted=1):
      """
         Like propagateArea, but using a postgres stored function.
      """
      sql = """select propagate_area(%s,%s,%s,%s)"""
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()   
      cursor.execute(sql, [node.segment.id, node.id, inserted, config.taylorDepth])
      transaction.commit_unless_managed()

   def propagateArea(self, node, config, inserted=1):
      """
         Propagate the area and other features up the score tree, balancing as needed using an AVL algorithm.
         
         For balancing, positive numbers are heavy on the left, negative numbers are heavy on the right.
         
         node - the node to start at (bottom-up traversal)
         config - an evo.config.Config object with property "shiftToDb"
         inserted - how many new levels have been added to the tree, 1 or 0. If 0, no balancing is needed.
         
      """
      from pyec.db.models import convertArray, UnsupportedBackendException
      
      if config.shiftToDb:
         try:
            self.propagateAreaInDb(node, config, inserted)
            return
         except UnsupportedBackendException:
            config.shiftToDb = False
      
      heightChange = inserted
      current = node
      children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [current.id]))
      while True:
         left = children[0]
         right = children[1]
         
         if inserted != 0:
            if current.balance > 1:
               if left.balance > 0:
                  self.rotateRight(current, config)
               else:
                  self.rotateLeft(left, config)
                  self.rotateRight(current, config)
               heightChange -= 1
            elif current.balance < -1:
               if right.balance < 0:
                  self.rotateLeft(current, config)
               else:
                  self.rotateRight(right, config)
                  self.rotateLeft(current, config)
               heightChange -= 1
         
         if abs(current.balance) <= 1:
            current.area = left.area + right.area
            current.taylor = left.taylor + right.taylor
            current.child_count = left.child_count + right.child_count + 1
            current.min_score = right.min_score
            current.max_score = left.max_score
         #   current.save() # defer to raw SQL
            from django.db import connection, transaction
            cursor = connection.cursor()
            sql = """
               UPDATE db_scoretree SET
                  area=%s, taylor=%s, child_count=%s, min_score=%s, max_score=%s, balance=%s
               WHERE id=%s;
            """
            cursor.execute(sql, [current.area, convertArray(current.taylor), current.child_count, current.min_score, current.max_score, current.balance, current.id])
            transaction.commit_unless_managed()
         
         children = list(self.raw("""select * from db_scoretree where parent_id=%s order by min_score desc""", [current.parent_id]))
         next = None
         if current.parent_id is not None:
            next = self.raw("""select * from db_scoretree where id=%s""", [current.parent_id])[0]
         
         if inserted != 0 and next is not None:
            onLeft = current.id == children[0].id
            oldbal = next.balance
            next.balance += onLeft and heightChange or -heightChange
            if oldbal < 0 and next.balance >= 0:
               heightChange = 0
            elif oldbal > 0 and next.balance <= 0:
               heightChange = 0
            next.height += heightChange
         #   current.parent.save()
         
         
         
         if next is not None:
            from django.db import connection, transaction
            cursor = connection.cursor()
            sql = """
               UPDATE db_scoretree SET height=%s, balance=%s WHERE id=%s;
            """
            cursor.execute(sql, [next.height, next.balance, next.id])
            transaction.commit_unless_managed()
         
         if next is None:
            break
         current = next
      
   def insert(self, point, config, stats):
      """
         Insert a new point into the score tree, then propagate area, taylor scores, and rebalance.
         Assumes the point has already been inserted into the partition tree
         
         point - the point to insert
         config - an evo.config.Config object with properties "shiftToDb", "taylorDepth", "taylorCenter", "selection"
         stats - an evo.trainer.RunStats object
      """
      stats.start("insert.import")
      from pyec.db.models import convertArray, Partition, ScoreTree, SeparationException
      stats.stop("insert.import")
      stats.start("insert.traverse")
      node = self.traverse(point, config)
      stats.stop("insert.traverse")
      stats.start("insert.main")
      lr = config.learningRate
      
      ns = [i+0. for i in xrange(config.taylorDepth)]
      fs = ns * 1
      if config.taylorDepth > 0:
         fs[0] = 1.0
         for i in xrange(config.taylorDepth - 1):
            fs[i+1] *= fs[i]
      ns = array(ns)
      fs = array(fs)
      center = config.taylorCenter      
      
      if node.point_id is None:
         node.point = point
         node.area = Partition.objects.get(point=point).area
         node.min_score = point.score
         node.max_score = point.score
         score = point.score * lr 
         taylor = nan_to_num(score ** ns) / fs
         taylor *= node.area
         taylor *= nan_to_num(exp(score) ** center) 
         node.taylor = nan_to_num(taylor)
         node.save()
         return
      
      
      other = node.point
      node.point = None
      
      if other.score > point.score:
         upPoint = other
         downPoint = point
         node.max_score = other.score
         node.min_score = point.score
      else:
         upPoint = point
         downPoint = other
         node.max_score = point.score
         node.min_score = other.score
      
      node.height = 1
      
      from django.db import connection, transaction
      cursor = connection.cursor()   
      
      cursor.execute("select area from db_partition where point_id=%s",[upPoint.id])
      upArea = float(cursor.fetchone()[0])
      cursor.execute("select area from db_partition where point_id=%s",[downPoint.id])
      downArea = float(cursor.fetchone()[0])
      
      
      score1 = upPoint.score * lr    
      score2 = downPoint.score * lr    
      taylor1 = (score1 ** ns) / fs
      taylor1 *= upArea
      taylor1 *= (exp(score1) ** center) 
      taylor2 = (score2 ** ns) / fs
      taylor2 *= downArea
      taylor2 *= (exp(score2) ** center)
      
      if config.selection == "proportional":
         if (abs(taylor1) < 1e-300).all() and (abs(taylor2) < 1e-300).all():
            node.point = other
            node.height = 0
            node.max_score = other.score
            node.min_score = other.score
            # node has not been saved to the DB, so we don't need to rollback
            #node.save()
            #transaction.rollback()
            raise SeparationException, "Zero taylor coeffs"
      """
      n1 = ScoreTree(
         segment=node.segment,
         point=upPoint,
         area = upArea.area,
         parent = node,
         max_score = upPoint.score,
         min_score = upPoint.score,
         taylor = taylor1
      )
      n1.save()
      n2 = ScoreTree(
         segment=node.segment,
         point=downPoint,
         area = downArea.area,
         parent = node,
         max_score = downPoint.score,
         min_score = downPoint.score,
         taylor = taylor2
      )
      n2.save()
      """
      
      sql = """
         UPDATE db_scoretree SET 
            point_id=NULL, height=1, max_score=%s, min_score=%s
         WHERE id=%s;
      """
      cursor.execute(sql, [float(node.max_score), float(node.min_score), node.id])
      
      
      sql = """
         INSERT INTO db_scoretree(
            segment_id, point_id, area, parent_id, max_score, min_score, 
            taylor, child_count, height, balance)
         VALUES
            (%s,%s,%s,%s,%s,%s,%s,0,0,0);   
      """
      cursor.execute(sql, [node.segment_id, upPoint.id, upArea, node.id, float(upPoint.score), float(upPoint.score), convertArray(taylor1)])
      
      sql = """
         INSERT INTO db_scoretree(
            segment_id, point_id, area, parent_id, max_score, min_score, 
            taylor, child_count, height, balance)
         VALUES
            (%s,%s,%s,%s,%s,%s,%s,0,0,0);   
      """
      
      cursor.execute(sql, [node.segment_id, downPoint.id, downArea, node.id, float(downPoint.score), float(downPoint.score), convertArray(taylor2)])
      transaction.commit_unless_managed()
      
      stats.stop("insert.main")
      stats.start("insert.propagate")
      self.propagateArea(node, config)
      stats.stop("insert.propagate")

   def resetTaylor(self, segment, temp, config):
      """
         Recompute the taylor coefficients on the Score tree.
         
         This should be done whenever temp gets more than 0.5 away from the taylor center for accuracy.
         
         Requires a loop through all points, but only needs to be done at a logarithmically often.
         
         segment - the segment to recompute
         temp - the new temperature center
         config - an evo.config.Config object with "shiftToDb", "taylorCenter", "taylorDepth"
         
         This method sets config.taylorCenter to temp when complete.
      """
      log.info("resetTaylor: segment %s, new center %s, old center %s" % (segment.id, temp, config.taylorCenter))
      from pyec.db.models import convertArray, parseArray, ScoreTree, UnsupportedBackendException
      if config.shiftToDb:
         try:
            self.resetTaylorInDb(segment, temp, config)
            return
         except UnsupportedBackendException:
            config.shiftToDb = False
      height = list(ScoreTree.objects.raw("""select * from db_scoretree where segment_id=%s order by height desc""", [segment.id]))
      if len(height) > 0:
         height = height[0].height
      else:
         height = 1
      
      ns = [i+0. for i in xrange(config.taylorDepth)]
      fs = ns * 1
      if len(fs) > 0:
         fs[0] = 1.0
         for i in xrange(config.taylorDepth - 1):
            fs[i+1] *= fs[i]
      ns = array(ns)
      fs = array(fs)
      center = config.taylorCenter 
      lr = config.learningRate
      from django.db import connection, transaction
      cursor = connection.cursor()
      for i in xrange(height + 1):
         currDepth = i
         for node in ScoreTree.objects.filter(height=currDepth):
            if node.point_id is not None:
               score = node.point.score * lr
               taylor = nan_to_num(score ** ns) / fs
               taylor *= node.area
               taylor *= nan_to_num(exp(score) ** center) 
               node.taylor = nan_to_num(taylor)
            else:
               sql = """select taylor from db_scoretree where parent_id=%s"""
               cursor.execute(sql, [node.id])
               children = cursor.fetchall()
               node.taylor = zeros(config.taylorDepth)
               for child in children:
                  node.taylor += parseArray(child[0])
            sql = """
               UPDATE db_scoretree SET taylor=%s WHERE id=%s
            """
            cursor.execute(sql, [convertArray(node.taylor), node.id])
      transaction.commit_unless_managed()
      config.taylorCenter = float(temp)
      
   def resetTaylorInDb(self, segment, temp, config):
      """
         Like resetTaylor, but using postgres stored functions
      """
      from django.db import connection, transaction
      from pyec.db.models import UnsupportedBackendException
      UnsupportedBackendException.maybeThrow(connection)
      cursor = connection.cursor()
      cursor.execute("""select max(height) from db_scoretree where segment_id=%s""", [segment.id])
      height = int(cursor.fetchone()[0])
      cursor.execute("""
            update db_scoretree 
            set taylor=compute_taylor(point_id, area, %s, %s, %s) 
            where point_id is not null and segment_id=%s
         """, [float(temp), float(config.learningRate), config.taylorDepth, segment.id])
      for i in xrange(height):
         currDepth = i+1
         cursor.execute("""
               update db_scoretree 
               set taylor=sum_taylor(segment_id, id, %s) 
               where segment_id=%s and height=%s and point_id is null
            """, [config.taylorDepth, segment.id, currDepth])
      config.taylorCenter = float(temp)
      transaction.commit_unless_managed()

