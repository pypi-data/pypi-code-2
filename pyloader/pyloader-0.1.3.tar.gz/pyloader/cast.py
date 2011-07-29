#!/usr/bin/env python

"""
cast strings to python objects
"""

class StringCastException(Exception):
  """raised on unsucessful cast"""

class StringCaster(object):
  """cast strings to other things"""
  # as yet unused

  def __init__(self, *casts):
    self.casts = casts

  def __call__(self, string):
    for cast in self.casts:
      try:
        return cast(string)
      except:
        continue
    return string

### casters

def str2bool(string):
  mapping = {'true': True,
             'True': True,
             'false': False,
             'False': False}
  return mapping[string]

def str2list(string, separator=None):
  string = string.rstrip(separator)
  return [i.strip() for i in string.split(separator)]

def str2args(string, separator=','):
  args = str2list(string, separator)
  _args = []
  kw = {}
  for arg in args:
    if '=' in arg:
      key, value = arg.split('=', 1)
      key = key.strip()
      value = value.strip()
      kw[key] = value
    else:
      _args.append(arg)
  return _args, kw

# convenience functions
casts = [int, float, str2bool, str2list, str2args]
cast = StringCaster(*casts)

# cast by type
cast_dict = dict([(i,i) for i in int, float])
cast_dict[bool] = str2bool
cast_dict[tuple] = cast_dict[list] = str2list

if __name__ == '__main__':
  import sys
  for arg in sys.argv[1:]:
    print cast(arg)
