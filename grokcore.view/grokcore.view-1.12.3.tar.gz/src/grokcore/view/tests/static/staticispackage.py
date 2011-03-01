"""
It is an error for the 'static' directory to be a python package:

  >>> import grokcore.view as grok
  >>> grok.testing.grok('grokcore.view.tests.static.staticispackage_fixture')
  Traceback (most recent call last):
    ...
  GrokError: The 'static' resource directory must not be a python package.
"""
