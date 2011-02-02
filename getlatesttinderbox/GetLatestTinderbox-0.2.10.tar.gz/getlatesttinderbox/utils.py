#!/usr/bin/env python

"""
utility functions for logparser
"""

import time
from dateutil.parser import parse

__all__ = ['str2ssepoch']

def str2ssepoch(string):
  """converts a string to seconds since epoch"""
  try:
    # see if this is already in seconds
    return int(string)
  except ValueError:
    date = parse(string)
    return int(time.mktime(date.timetuple()))

if __name__ == '__main__':
  # mostly for testing
  import sys
  args = sys.argv[1:]
  if not args:
    print str2ssepoch(time.time())
  for arg in args:
    print str2ssepoch(arg)
