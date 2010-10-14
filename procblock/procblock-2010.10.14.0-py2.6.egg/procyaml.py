"""
procyaml

Process YAML files to make them easier to write for procblock.

Specially, add __import_%(key)s tags, so we can embed YAML files inside of
each other, and order our data a bit more sanely.

ImportYaml() does the __import_ thing.

LoadYaml() does caching.  TODO(g): Mix this with that.

TODO(g): ImportYaml should cache, but needs to remember all the files it __load
    or __import imported, so that we can test all these files for changes as
    well.  Any of these files changing should invalidate the cache.
"""


import os
import yaml
import stat
import logging

import unidist
from unidist import stack
from unidist.log import log
from unidist import sharedstate


# All YAML files we load can be cached and tested here
YAML_CACHE = {}
YAML_CACHE_TIME = {}


def Save(path, data):
  """Save this data to this path, in YAML format.
  Uses temp file to avoid clobbering the original and failing to complete.
  """
  temp_file = '%s.tmp' % path
  fp = open(temp_file, 'w')
  yaml.dump(data, fp)
  fp.close()
  os.rename(temp_file, path)


def Load(path):
  """**Deprecating in favor of ImportYaml(), which can recursively import.**
  
  TODO(g): Decommission LoadYaml from use...  Redundant in this module.
  
  Args:
    path: string, file to load
  """
  return LoadYaml(path)


def LoadYaml(path):
  """**Deprecating in favor of ImportYaml(), which can recursively import.**
  
  Wraps loading of files, so they can be cached, and the cache can be
  updated.
  
  Args:
    path: string, file to load
  """
  global YAML_CACHE
  
  if type(path) != str:
    log('Path is not a string: %s: %s' % (stack.Mini(4), path), logging.ERROR)
  
  # If we have the path in cache, and the file change time hasnt changed,
  #   return the cached value
  if path in YAML_CACHE:
    if os.stat(path)[stat.ST_MTIME] == YAML_CACHE_TIME[path]:
      return YAML_CACHE[path]
  
  # Load data
  try:
    fp = open(path, 'r')
    data = yaml.load(fp.read())
    fp.close()
  except TypeError:
    log('Failed to load YAML file: %s' % path, logging.ERROR)
    raise
  
  if data != None:
    # Cache data
    YAML_CACHE[path] = data
    timestamp = os.stat(path)[stat.ST_MTIME]
    YAML_CACHE_TIME[path] = timestamp
    
    # Save this in our shared state.  Use this instead of the cache?
    sharedstate.Set('__internals.yaml', path, (data, timestamp))
  
  return data


def ImportYaml_ImportKey(data, cwd):
  """Recursive function to import keys into a YAML dictionary."""
  for key in data.keys():
    # If this key is an import key
    if key.startswith('__import__'):
      (_, import_key) = key.split('__import__', 1)
      
      log('Importing key: %s: %s' % (import_key, data[key]))
      
      #TODO(g): Process the filename, if it's not absolute, test local, and
      #   then localize off the filename's path
      import_filename = data[key]
      
      # If the import_filename is not an existing absolute or relative path
      if not os.path.isfile(import_filename):
        # If this is an absolute path, then we cant load it
        if import_filename.startswith('/'):
          raise Exception('ImportYaml: Cannot import key YAML: %s: %s: Absolute path file not found' % (key, import_filename))
        # Else, append on our 
        else:
          import_filename = '%s/%s' % (cwd, import_filename)
          
          if not os.path.isfile(import_filename):
            raise Exception('ImportYaml: Cannot import key YAML: %s: %s: Appending to current working directory failed' % (key, import_filename))
      
      # Import the YAML
      import_data = ImportYaml(import_filename, cwd=cwd)
      
      # Delete the import key rule, keep it clean
      del data[key]
      
      # If this key already exists, and is a dictionary, update
      if import_key in data and type(data[import_key]) == dict and type(import_data) == dict:
        data[import_key].update(import_data)
      
      # Else, overwright the key
      else:
        data[import_key] = import_data
    
    # Else, this is a load directive, and data will be brought into this tag
    #   instead of imported into a new specified tag
    elif key == '__load':
      # Import the __load data
      load_data = ImportYaml(data[key], cwd=cwd)
      
      # Update the current data with the loaded data
      data.update(load_data)
      
      # Remove the load key, no longer needed
      del data[key]
    
    # Else, if this is a dictionary value, then run it through the importer too
    elif type(data[key]) == dict:
      
      ImportYaml_ImportKey(data[key], cwd)


def Import(filename, cwd=None):
  """TODO(g): Migrate usage to this?  It's obvious it's a YAML file..."""
  return ImportYaml(filename, cwd=cwd)


def ImportYaml(filename, cwd=None):
  """Import this YAML file, and import recursively any sections marked with
  __import__name, where "name" will be updated as a dictionary, or replaced
  if not a dictionary.
  
  Args:
    filename: string, name of file to load
    cwd: string (optional), if present this is the current working directory
        of the first imported file
  
  Returns: data, typically a dictionary.  Contents of YAML file.
  """
  # Get timestamp, to check against our cache time
  timestamp = os.stat(filename)[stat.ST_MTIME]
  
  # If we have this cached, and it's timestamp is the same as the file's
  #NOTE(g): Any difference, even older, is a change that should be expected to
  #   be adopted.  Going forward only intrudes more complexity than always
  #   respecting a new file (provided it doesnt have the same timestamp, because
  #   were not wasting CPU cycles doing a digest test).  If needed, wrap this
  #   and make a default=Off option.
  if sharedstate.KeyExists('__internals.yaml', filename):
    (cache_data, cache_timestamp) = sharedstate.Get('__internals.yaml', filename)
    if cache_timestamp == timestamp:
      return cache_data
  
  log('Importing YAML: %s' % filename)
  fp = open(filename)
  data = yaml.load(fp)
  fp.close()
  
  # If the data is empty, return an empty dict
  if data == None:
    return {}
  
  if cwd == None:
    cwd = os.path.dirname(filename)
  
  # If the data is a dictionary, we need to check the keys for import rules
  if type(data) == dict:
    ImportYaml_ImportKey(data, cwd)
  #
  #else:
  #  print '  Type: %s' % type(data)
  
  # Save timestamp, for caching
  timestamp = os.stat(filename)[stat.ST_MTIME]
  
  # Save this in our shared state.  Use this instead of the cache?
  sharedstate.Set('__internals.yaml', filename, (data, timestamp))
  
  return data


def WalkTreeExtractTag(data, tag, extract_function):
  """Data the data tree looking for a tag.
  
  Args:
    data: arbitrary data to walk, really only works on dicts/sequences combos,
        but accepts any structure, and reads tags only from dicts (obviously)
    tag: string, the key to search for in whatever dicts are inside this
        arbitrarily nested data
    extract_function: function, a function of the arg format:
        Func(data, collected)
        Where data is the data found with the key of the tag variable, and
        collected is the dict we are passing around to collect results
  
  Returns: dict, keyed on whatever the extract_function used to store the data,
      values are whatever the extract data chose to store.
  """
  collected = {}
  
  # If the data is a dict or ThreadSafeDict
  if type(data) == dict or isinstance(data, unidist.threadsafedict.ThreadSafeDict):
    for key in data:
      # If this is a TS Collect block, then extract the TS data items and store
      #   them by their TS data path names in collected
      if key == tag:
        extract_function(data[key], collected)
      
      # If this could be another container, recurse
      elif type(data[key]) == dict or isinstance(data[key], unidist.threadsafedict.ThreadSafeDict):
        collected.update(WalkTreeExtractTag(data[key], tag, extract_function))
      
      # Recurse if it's a sequence too
      elif type(data[key]) in (list, tuple) or isinstance(data[key], unidist.threadsafelist.ThreadSafeList):
        collected.update(WalkTreeExtractTag(data[key], tag, extract_function))
  
  # Else, if the data is a sequence or ThreadSafeList
  elif type(data) in (list, tuple) or isinstance(data, unidist.threadsafelist.ThreadSafeList):
    for item in data:
      # If this could be another container, recurse
      if type(item) == dict or isinstance(item, unidist.threadsafedict.ThreadSafeDict):
        collected.update(WalkTreeExtractTag(item, tag, extract_function))
      
      # Recurse if it's a sequence too
      elif type(item) in (list, tuple) or isinstance(item, unidist.threadsafelist.ThreadSafeList):
        collected.update(WalkTreeExtractTag(item, tag, extract_function))
  
  return collected
