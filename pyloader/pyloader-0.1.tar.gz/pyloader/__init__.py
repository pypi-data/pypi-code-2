#!/usr/bin/env python

"""
load modules and their attributes from a string
"""

import imp
import os

def import_dotted_path(module):
  path = module.split('.')
  module = __import__(module)
  for name in path[1:]:
    module = getattr(module, name)
  return module

def load(string):
  """loads a string and returns a python object"""

  try:
    if ':' in string:
      path, target = string.split(':', 1)
      if os.path.isabs(path) and os.path.exists(path):
        # path to file
        module = imp.load_source(path, path)
      else:
        module = import_dotted_path(path)
      obj = module
      while '.' in target:
        attr, target = target.split('.', 1)
        obj = getattr(obj, attr)
      obj = getattr(obj, target)
      return obj
    else:
      # module: dotted path
      return import_dotted_path(string)
  except:
    print string
    raise

  # TODO: entry points

if __name__ == '__main__':
  import sys
  for i in sys.argv[1:]:
    print load(i)
