#!/usr/bin/python
#coding:utf-8

import sys,types
from StringIO import StringIO

class Redirect:
     def __init__(self):
          sys.stdout = StringIO()
          self.stdout = sys.stdout

     def getitem(self):
          if self.check():
               item = sys.stdout.getvalue()
               self.stdout.close()
               sys.stdout = sys.__stdout__
          return item

     def getitems(self):
          if self.check():
               item = sys.stdout.getvalue()
               items = item.split("\n")
               self.stdout.close()
               sys.stdout = sys.__stdout__
          return items

     def quit(self):
          if self.check(): self.stdout.close();sys.stdout = sys.__stdout__
          


     def check(self):
          if isinstance(self.stdout,types.InstanceType): return True
          else:return False
          
