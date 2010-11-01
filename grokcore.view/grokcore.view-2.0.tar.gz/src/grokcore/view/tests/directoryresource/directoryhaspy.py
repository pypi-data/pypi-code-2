"""
When a directory resource is declared, it is not allowed to have a python
module by the same name::

  >>> import grokcore.view as grok
  >>> grok.testing.grok(
  ...     'grokcore.view.tests.directoryresource.directoryhaspy_fixture')
  Traceback (most recent call last):
    ...
  GrokError: A package can not contain both a 'foo' resource directory
  and a module named 'foo.py'
"""
