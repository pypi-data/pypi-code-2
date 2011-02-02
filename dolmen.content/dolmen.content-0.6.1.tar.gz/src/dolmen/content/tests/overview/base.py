"""
Base components
===============

This test's purpose is to test simple components instanciation
after grokking.

We first declare our components and grok them::

  >>> import dolmen.content
  >>> from grokcore.component.testing import grok_component

  >>> class Mammoth(dolmen.content.Content):
  ...   dolmen.content.name('mammoth')

  >>> grok_component('mammoth', Mammoth)
  True

  >>> class Cave(dolmen.content.Container):
  ...   dolmen.content.name('cave')

  >>> grok_component('cave', Cave)
  True

  >>> class HunterQuiver(dolmen.content.OrderedContainer):
  ...   dolmen.content.name('quiver')

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
