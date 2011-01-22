"""
It is an error for the 'static' directory to be a python package:

  >>> grok.testing.grok('five.grok.tests.all.staticispackage')
  Traceback (most recent call last):
    ...
  GrokError: The 'static' resource directory must not be a python package.

When a package contains a 'static' resource directory, it must not also contain
a module called 'static.py':

  >>> grok.testing.grok('five.grok.tests.all.statichaspy')
  Traceback (most recent call last):
    ...
  GrokError: A package can not contain both a 'static' resource directory and a module named 'static.py'
"""

from five import grok
