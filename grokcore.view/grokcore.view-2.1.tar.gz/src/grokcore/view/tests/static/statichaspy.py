"""
When a package contains a 'static' resource directory, it must not also contain
a module called 'static.py':

  >>> import grokcore.view as grok
  >>> grok.testing.grok('grokcore.view.tests.static.statichaspy_fixture')
  Traceback (most recent call last):
    ...
  GrokError: A package can not contain both a 'static' resource directory
  and a module named 'static.py'
"""
