#!/usr/bin/env python

def import_path(module):
  path = module.split('.')
  module = __import__(path[0])
  for name in path[1:]:
    module = getattr(module, name)
  return module

if __name__ == '__main__':
  import sys
  for i in sys.argv[1:]:
    print import_path(i)
