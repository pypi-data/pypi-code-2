from django.db import models
from numpy import *
import numpy
from string import Template, Formatter
from pyec.distribution.bayes.net import BayesNet
import managers
from pyec.constants import *
from pyec.util.TernaryString import TernaryString
from pyec.config import Config
import binascii
import cPickle


from time import time

import logging
logger = logging.getLogger(__file__)

seterr(all='ignore')



class UnsupportedBackendException(Exception):
   """
      Thrown when an attempted is made to call PL/PGSQL stored functions
      when the backend is not postgres.
   """
   @classmethod
   def maybeThrow(cls, connection):
      if connection.settings_dict['ENGINE'] != POSTGRES_BACKEND:
         raise cls, "This function requires a Postgres backend"

class SeparationException(Exception):
   pass

def convertArray(value):
   """
      Convert a numpy array or a list to Postgres-style array
      text for insertion into a Postgres array field or a text
      field in other databases.
   """
   if isinstance(value, ndarray) or isinstance(value, list):
      return '{' + ",".join([convertArray(val) for val in value]) + '}'
   elif value is not None:
      return str(value)
   else:
      return None
      
def parseArray(value):
   """
      Convert a Postgres-style array string into a numpy array recursively.
   """
   if value is not None:
      if isinstance(value, ndarray):
         return value
      elif isinstance(value, list):
         return array(value)
      elif isinstance(value, basestring):
         value = value.strip("'")
         value = value.strip('"')
         if len(value) == 0:
            return None
         elif value == '{}':
            return array([])
         elif value[0] == '{' and value[-1] == '}':
            return array([parseArray(val) for val in value[1:-1].split(',')])
         else:
            return float(value.strip())
      else:
         return float(value)
   else:
      return None

class RealArrayField(models.TextField):
   """
      A field to store n-dimensional arrays of real strings.
      Maps to type "double precision[]" on postgres, to "text"
      on other databases.
   """
   __metaclass__ = models.SubfieldBase

   """Special Field to store an array as a string"""
   def db_type(self, connection):
      if connection.settings_dict['ENGINE'] == POSTGRES_BACKEND:
         return 'double precision[]'
      return 'text'
      
   def to_python(self, value):
      return parseArray(value)

   def get_prep_value(self, value):
      return convertArray(value)

class BinaryField(models.TextField):
   """
      Field to store a sequence of bytes as a string
      Converts to a pyec.util.TernaryString.TernaryString
   """
   __metaclass__ = models.SubfieldBase
   
   def db_type(self, connection):
      return "text"
      
   def to_python(self, value):
      if value:
         if isinstance(value, TernaryString):
            return value
         numBits = int(ceil(numpy.log2(10) * (len(str(value)) + 1))) 
         base = long(value)
         known = (1L << (numBits + 1)) - 1
         return TernaryString(base, known)
      else:
         return None
         
   def get_prep_value(self, value):
      return (value is not None) and str(value) or value

class BayesNetField(models.TextField):
   """
      Field to store a bayes net as a string.
      
      Note that conversion of the net is dependent
      for the time being on an evo.config.Config object.
      
      This config object should be configured on the class
      using the set_configuration() method.
      
      If multiple concurrent threads need different
      types of nets in the same process, this will 
      have to be refactored so that the network representation
      in the database is not dependent on the config.
   """
   config = None
   
   __metaclass__ = models.SubfieldBase
   
   
   @classmethod
   def set_configuration(cls, cfg):
      cls.config = cfg
   
   def db_type(self, connection):
      return 'text'
      
   def to_python(self, value):
      if value:
         net = BayesNet.parse(str(value), self.__class__.config)
         return net
      else:
         return None
         
   def get_prep_value(self, value):
      return value and str(value) or value
      

class ConfigField(models.TextField):
   """
      Field to store a pyec.config.Config object
   """
   __metaclass__ = models.SubfieldBase
   
   def db_type(self, connection):
      return "text"
      
   def to_python(self, value):
      if value:
         if isinstance(value, Config):
            return value
         return cPickle.loads(str(value))
      else:
         return None
         
   def get_prep_value(self, value):
      try:
         return (value is not None) and cPickle.dumps(value) or value
      except:
         return None

class Segment(models.Model):
   """
      A Segment provides logical separation within the database 
      for separate runs of optimization.
      
      A single segment corresponds to a single run of the optimization algorithm.
   """
   name = models.CharField(max_length=256, unique=True)
   config = ConfigField(null=True)
   totalprob = models.FloatField(default=0.0)

   objects = managers.SegmentManager()




class Point(models.Model):
   """
      Database representation of a candidate solution.
      
      The field "point" stores real arrays.
      The field "bayes" stores Bayesian networks.
      The field "binary" stores binary strings (as evo.util.TernaryString.TernaryString objects)
      
      score - the raw fitness of the current point
      probindex - a cumulative probability vector, used by PointManager.sample()
      count - the number of points in the general area; see SegmentManager.updateCounts()
      segment - the Segment to which the point belongs
      alive - whether this point should be included in computation of the probindex  
   """
   point = RealArrayField(null=True)
   bayes = BayesNetField(null=True)
   binary = BinaryField(null=True)
   score = models.FloatField()
   probindex = models.FloatField(default=0.0)
   count = models.PositiveIntegerField(default=0)
   segment = models.ForeignKey(Segment, db_index=True)
   alive = models.BooleanField(default=True, db_index=True)

   objects = managers.PointManager()
   
   @property
   def separable(self):
      """
         Get a representation of the point suitable for insertion in the Partition tree.
         
         TODO - representation caching
         
         Called by PartitionManager.separate()
      """
      if self.point is not None: 
         return self.point
      elif self.bayes is not None:
         return self.bayes.edgeBinary()
      elif self.binary:
        if self.segment.config.binaryPartition:
            return self.binary
        else:
            return self.binary.toArray(self.segment.config.dim)
      else:
         return None

class Distance(models.Model):
   """
      Store distances between Point objects as a cache.
      
      Not currently used
   """
   fro = models.ForeignKey(Point, related_name='from_set')
   to = models.ForeignKey(Point, related_name='to_set')
   distance = models.FloatField()
   
   class Meta:
      unique_together = ("fro","to")

class Partition(models.Model):
   """
     A partition tree, one per segment. The root node should have parent=None.
     
     index - the index in point.separable that is separated by this node
     upper - the upper boundary of the partition at point.separable[index]
     lower - the lower boundary of the partition at point.separable[index]
     area  - the area of the partition
     point - the point residing in this partition if a leaf, null otherwise
     parent - the parent node
     segment - the segment for the tree
   """
   upper = models.FloatField()
   lower = models.FloatField()
   index = models.PositiveIntegerField()
   key = BinaryField(null = True)
   segment = models.ForeignKey(Segment, db_index=True)
   parent = models.ForeignKey('Partition', null=True, db_index=True)
   point = models.OneToOneField(Point, null=True, db_index=True)
   area = models.FloatField(default=1.0)
   score_sum = models.FloatField(default=0.0, null=True)

   objects = managers.PartitionManager()
   
      
class ScoreTree(models.Model):
   """
      A balanced binary tree with propagated areas and taylor coefficients
      for evolutionary annealing, suitable for sampling and insertion in logarithmic time.
      The left child has the higher score
   """
   segment = models.ForeignKey(Segment, db_index=True)
   parent = models.ForeignKey('ScoreTree', null=True, db_index=True)
   point = models.OneToOneField(Point, null=True, db_index=True)
   area = models.FloatField(default=1.0)
   min_score = models.FloatField(default=-1e100)
   max_score = models.FloatField(default=1e100)
   child_count = models.PositiveIntegerField(default=1)
   taylor = RealArrayField(null=True)
   height = models.PositiveIntegerField(default=0, db_index=True)
   balance = models.IntegerField(default=0)

   objects = managers.ScoreTreeManager()


