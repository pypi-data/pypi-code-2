
"""
    This is a demo view to show the contents
    of one tagged item.
"""

from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from five import grok

from ..interfaces import ITagManager, IPersonalTagsSettings

class ListTags(grok.View):
    grok.name('personaltags_listtags')
    grok.context(Interface)
    grok.require('zope2.View')

    tag = 'Not Provided'

    def __init__(self, context, request):
        super(ListTags, self).__init__(context, request)
        if 'tag' in self.request.form:
            self.tag = self.request.form.get('tag', 'Not Provided')
        self.title = "Items for : %s" % self.tag

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPersonalTagsSettings)
        self.adapter = getAdapter(self.context, ITagManager, name=settings.storage)

    def tagged(self):
        """This is a catalog brains list"""
        return self.adapter.getItemsForTag(self.tag)

