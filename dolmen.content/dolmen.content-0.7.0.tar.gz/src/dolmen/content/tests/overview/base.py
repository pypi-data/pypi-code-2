"""
Base components
===============

This test's purpose is to test simple components instanciation
after grokking.

We first declare our components and grok them::

  >>> import dolmen.content
  >>> from zope.schema import TextLine
  >>> from zope.interface import Interface
  >>> from grokcore.component.testing import grok_component

  >>> class TitleSchema(Interface):
  ...     title = TextLine(
  ...       title=u'Title',
  ...       required=True,
  ...       default=u'')

  >>> class Mammoth(dolmen.content.Content):
  ...   dolmen.content.name('mammoth')
  ...   dolmen.content.schema(TitleSchema)

  >>> grok_component('mammoth', Mammoth)
  True

  >>> class Cave(dolmen.content.Container):
  ...   dolmen.content.name('cave')
  ...   dolmen.content.schema(TitleSchema)

  >>> grok_component('cave', Cave)
  True

  >>> class HunterQuiver(dolmen.content.OrderedContainer):
  ...   dolmen.content.name('quiver')
  ...   dolmen.content.schema(TitleSchema)

  >>> grok_component('quiver', HunterQuiver)
  True

We now instanciate them with and without arguments::

  >>> gunther = Mammoth()
  >>> gunther
  <dolmen.content.tests.overview.base.Mammoth object at ...>

  >>> manfred = Mammoth(title=u'Manfred the Impetuous')
  >>> manfred
  <dolmen.content.tests.overview.base.Mammoth object at ...>
  >>> manfred.title
  u'Manfred the Impetuous'

  >>> grotto = Cave()
  >>> grotto
  <dolmen.content.tests.overview.base.Cave object at ...>

  >>> icecave = Cave(title=u'An icy cave')
  >>> icecave.title
  u'An icy cave'

  >>> quiver = HunterQuiver()
  >>> quiver
  <dolmen.content.tests.overview.base.HunterQuiver object at ...>

  >>> grokquiver = HunterQuiver(title=u'A mammoth hunter quiver')
  >>> grokquiver.title
  u'A mammoth hunter quiver'

"""
