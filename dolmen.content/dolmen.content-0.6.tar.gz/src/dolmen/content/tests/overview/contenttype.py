"""
Content type
============

A ``dolmen.content`` item, when grokked, gets a `__content_type__`
attributes, that can be useful to sort/classify/index the objects.

This `__content_type__` is computed from the `name` directive or the
class name, if no `name` directive is used::

  >>> from dolmen.content import Content
  >>> from grokcore.component import testing


No directive
------------

  >>> class SomeContent(Content):
  ...    pass

  >>> SomeContent.__content_type__
  Traceback (most recent call last):
  ...
  AttributeError: type object 'SomeContent' has no attribute
  '__content_type__'

  >>> testing.grok_component('somecontent', SomeContent)
  True

  >>> print SomeContent.__content_type__
  SomeContent


Directive
---------

  >>> from dolmen.content import name

  >>> class AnotherContent(Content):
  ...   name('my nice content')

  >>> AnotherContent.__content_type__
  Traceback (most recent call last):
  ...
  AttributeError: type object 'AnotherContent' has no attribute
  '__content_type__'

  >>> testing.grok_component('another', AnotherContent)
  True

  >>> print AnotherContent.__content_type__
  my nice content


Heritage
--------

  >>> class YetAnotherContent(AnotherContent):
  ...   name('I do override the parent value')

  >>> print YetAnotherContent.__content_type__
  my nice content

  >>> testing.grok_component('yetanother', YetAnotherContent)
  True

  >>> print YetAnotherContent.__content_type__
  I do override the parent value


Utility function
----------------

  >>> from dolmen.content import get_content_type

  >>> print get_content_type(YetAnotherContent)
  I do override the parent value

  >>> obj = AnotherContent()
  >>> print get_content_type(obj)
  my nice content

  >>> toto = object()
  >>> print get_content_type(toto)
  None

"""
