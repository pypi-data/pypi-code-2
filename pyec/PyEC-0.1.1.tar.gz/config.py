from numpy import *
import copy
import os, subprocess
import os.path
import tempfile

def setup_environment(**kwargs):
   """
     Set up the database context via environment variables.
     
     Keyword args:
    
        inmemory - boolean, if true, then use SQLite in memory
        backend - a django backend; if present use the specified backend
        db - the name of the database; if SQLite then .db will be added
        sqlite - the path to sqlite databases
   """
   dbName = 'evo'
   inmem = False
   sqlite = False
   os.environ['DJANGO_SETTINGS_MODULE'] = 'pyec.settings'
   for key, val in kwargs.iteritems():
      if key == 'inmemory':
         if val:
            inmem = True
            sqlite = True
            os.environ["EVO_DATABASE"] = ':memory:'
            os.environ["EVO_SQLITE"] = ''
      elif key == 'backend':
         os.environ["EVO_BACKEND"] = val
      elif key == 'db':
         os.environ["EVO_DATABASE"] = val
         dbName = val
      elif key == 'sqlite':
         sqlite = True
         os.environ["EVO_BACKEND"] = 'django.db.backends.sqlite3'
         os.environ["EVO_SQLITE"] = val
         inmem = True
   
   if inmem:
      os.environ["EVO_DATABASE"] = ':memory:'            
   from django.core import management
   psql = (not kwargs.has_key('backend') or "postgres" in kwargs['backend']) and (not inmem) and not sqlite
   if psql:
      fname = os.path.dirname(__file__)
      fname = os.path.join(fname,'db','sql','createPostgresDb.sh')
      subprocess.check_call([fname, dbName])
   management.call_command('syncdb', verbosity=0, interactive=False)
   if psql:
      fname = os.path.dirname(__file__)
      fname = os.path.join(fname,'db','sql','postgres.sql')
      infile = open(fname)
      subprocess.check_call(['psql','-U','evo',dbName], stdin=infile)
      infile.close()

def shutdown_environment(**kwargs):
   dbName = 'evo'
   inmem = False
   sqlite = False
   path = ''
   for key, val in kwargs.iteritems():
      if key == 'db':
         dbName = val
      elif key == 'sqlite':
         path = val
         sqlite = True
      elif key == 'inmemory':
         inmem = True

   if not inmem and sqlite:
      # save memory database to file
      fname = os.path.join(path, dbName + ".db")
      if not os.path.exists(fname):
         f = open(fname, "w")
         f.close()
      create_sqlite_db(path, dbName)
      # attach new db
      from django.db import connection, transaction
      cursor = connection.cursor()
      cursor.execute("""ATTACH DATABASE %s AS backup""", [fname])
      cursor.execute("""INSERT INTO backup.db_segment SELECT * FROM db_segment""", [])
      cursor.execute("""INSERT INTO backup.db_scoretree SELECT * FROM db_scoretree""", [])
      cursor.execute("""INSERT INTO backup.db_partition SELECT * FROM db_partition""", [])
      cursor.execute("""INSERT INTO backup.db_point SELECT * FROM db_point""", [])
      transaction.commit_unless_managed()
      cursor.execute("""DETACH backup""",[])
      transaction.commit_unless_managed()

def create_sqlite_db(path,name):
   os.environ['EVO_SQLITE'] = path
   os.environ['EVO_DATABASE'] = name
   subprocess.Popen(['python', os.path.join(os.path.dirname(__file__),'manage.py'), 'syncdb','--noinput','--verbosity', '0']).wait() 

class Config(object):
   def __get__(self, key):
      if not self.__dict__.has_key(key):
         return None
      return self.__dict__[key]

   def __set__(self, key, val):
      self.__dict__[key] = val

      
class ConfigBuilder(object):
   registry = {}
   registryKeys = []
   
   def __init__(self, algcls):
      self.cfg = Config()
      self.cfg.recording = False
      self.cfg.bounded = True
      self.cfg.segment = 'test'
      self.cfg.activeField = 'point'
      self.cfg.binaryPartition = False
      self.algcls = algcls
   
   def postConfigure(self,cfg):
      pass
   
   def configure(self, generations, populationSize, dimension=1, function=None):
      cfg = copy.copy(self.cfg)
      cfg.generations = generations
      cfg.populationSize = populationSize
      cfg.dim = dimension
      if function: cfg.function = function
      if function and self.__class__.registry.has_key(function):
         cfg.function = function
         print self.__class__.registry[function]
         for key,val in zip(self.__class__.registryKeys, self.__class__.registry[function]):
            setattr(cfg, key, val)
      self.postConfigure(cfg)
      return self.algcls(cfg)
   
   @classmethod      
   def register(cls, name, params):
      cls.registry[name] = params
