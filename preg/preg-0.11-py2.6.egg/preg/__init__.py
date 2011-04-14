#!/usr/bin/env python

import os
import sys


class ExtensionFilter(object):
  def __init__(self, extensions):
    self.extensions = extensions

  def __call__(self, path):
    return os.path.splitext(path)[1].lower() in self.extensions


class NoMatchFilter(object):
  def __init__(self, match):
    self.match = match

  def __call__(self, path):
    return self.match not in path



class Searcher(object):
  def __init__(self, filters = None):
    self.filters = filters or []

  def display_result(self, search_for, full_path, result):
    print full_path
    print result


  def search_file(self, search_for, full_path):
    for line in open(full_path).readlines():
      if search_for in line:
        self.display_result(search_for, full_path, line)
  
  def preg(self, search_for, paths):
    for path in paths:
      for root, dirs, files in os.walk(path):
        for f in files:
          full_path = os.path.join(root, f)
          if not any((e(full_path) == False for e in self.filters)):
            self.search_file(search_for, full_path)


def main():
  if len(sys.argv) == 2:
    search_for = sys.argv[1]
    paths = [os.getcwd()]
  elif len(sys.argv) > 3:
    search_for = sys.argv[1]
    paths = sys.argv[2:]
  else:
    print "not very good arguments"

  filters = []
  preg_class = Preg
  settings_path = os.path.join(os.path.expanduser("~"), ".pregrc.py")
  if os.path.exists(settings_path):
    # Give the config file access to the "filters" variable
    execfile(settings_path, globals(), locals())

  a = preg_class(filters = filters)
  a.search(search_for, paths)

if __name__ == "__main__":
  main()




