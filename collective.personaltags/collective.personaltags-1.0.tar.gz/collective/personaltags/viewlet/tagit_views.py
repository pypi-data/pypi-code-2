"""
    Views for the tagitwidget to use

"""
from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from five import grok

from ..interfaces import ITagManager, IPersonalTagsSettings

class AddTag(grok.View):
    grok.name('collective.personaltags.addtag')
    grok.context(Interface)
    grok.require('zope2.View')

    def __call__(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPersonalTagsSettings)
        adapter = getAdapter(self.context, ITagManager, name=settings.storage)
        adapter.addTag(self.request.form['tag'])
    def render(self):
        pass

class DeleteTag(grok.View):
    grok.name('collective.personaltags.deletetag')
    grok.context(Interface)
    grok.require('zope2.View')

    def __call__(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IPersonalTagsSettings)
        adapter = getAdapter(self.context, ITagManager, name=settings.storage)
        adapter.deleteTag(self.request.form['tag'])
    def render(self):
        pass
