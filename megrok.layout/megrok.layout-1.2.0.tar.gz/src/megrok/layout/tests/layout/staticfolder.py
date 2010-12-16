"""
  >>> from megrok.layout import ILayout
  >>> from zope.component import getMultiAdapter
  >>> from zope.publisher.browser import TestRequest
  >>> request = TestRequest()
  >>> mongo = Dummy()
  >>> mylayout = getMultiAdapter((request, mongo), ILayout)
  >>> mylayout.static
  <grokcore.view.components.DirectoryResource object at ...>
  >>> mylayout.static['empty.js']
  <zope.browserresource.file.FileResource object at ...>
"""

import grokcore.component as grok
from megrok.layout import Layout


class Dummy(grok.Context):
    pass


class LayoutWithResources(Layout):

    def render(self):
        return ""
