
"""
    Show / Hide / Delete tags
"""

from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility

from plone.registry.interfaces import IRegistry

from five import grok

from ..interfaces import ITagManager, IPersonalTagsSettings

class ManageTags(grok.View):
    grok.name('personaltags_manage')
    grok.context(Interface)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(ManageTags, self).__init__(context, request)

        registry = getUtility(IRegistry)
        settings = self.settings = registry.forInterface(IPersonalTagsSettings)
        self.adapter = getAdapter(self.context, ITagManager, name=settings.storage)

    def system_tags(self):
        tagInfo = self.adapter.getTagsAndStatus()
        rv = [tag for tag in tagInfo if tag['system'] == True]
        return sorted(rv, key=lambda rec: rec['tag'])

    def non_system_tags(self):
        tagInfo = self.adapter.getTagsAndStatus()
        rv = [tag for tag in tagInfo if tag['system'] == False]
        return sorted(rv, key=lambda rec: rec['tag'])

    @property
    def user(self):
        return self.request.AUTHENTICATED_USER.getUserName()

class DeleteTag(grok.View):
    grok.name('personaltags_manage_callback')
    grok.context(Interface)
    grok.require('zope2.View')

    def __call__(self):
        action = self.request.get('action', None)
        tagname = self.request.get('tagname', None)
        if action is None or tagname is None: 
            return

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPersonalTagsSettings)
        adapter = getAdapter(self.context, ITagManager, name=settings.storage)

        if action == 'show':
            adapter.confShow(tagname)
        elif action == 'hide':
            adapter.confHide(tagname)
        elif action == 'delete':
            adapter.confDelete(tagname)

    def render(self):
        pass
