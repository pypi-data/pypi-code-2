from zope.component import queryAdapter
from plone.memoize.instance import memoize

from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from raptus.contentflow.interfaces import IContentFlowProvider, IContentFlowProperties

class XML(BrowserView):
    """ The XML holding the data for flash
    """
    template = """<?xml version="1.0" encoding="utf-8"?>
<coverflow
%(properties)s
  >
%(items)s
</coverflow>
"""
    item_template = """  <cover>
    <img>%(img)s</img> 
    <title>%(title)s</title>
    <link>%(url)s</link>
  </cover>"""

    def __call__(self):
        self.request.RESPONSE.setHeader('Content-Type','text/xml')
        return self.template % {'properties': self.properties(),
                                'items': self.items()}

    @memoize
    def items(self):
        provider = queryAdapter(self.context, interface=IContentFlowProvider)
        if not provider:
            return None
        items = [self.item_template % item for item in provider()]
        return '\n'.join(items)
    
    @memoize
    def properties(self):
        provider = queryAdapter(self.context, interface=IContentFlowProperties)
        if not provider:
            return ''
        return '\n'.join(['  %s="%s"' % property for property in provider()])
