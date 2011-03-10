"""
    This is a widget based on the tagit jquery plugin...

    http://levycarneiro.com/projects/tag-it/example.html

    This tool allows a user to select options from a list
    same as plone.formwidget.autocomplete.

    However, it allows the user to add new words to the list.

    Also, my initial use case does not require a large number
    of options, so I will include the options inline.
"""

from five import grok

from zope.interface import Interface
from zope.component import getAdapter
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

from plone.app.layout.viewlets import common as base

from ..interfaces import ITagManager, IPersonalTagsSettings

class TagIt(base.ViewletBase):

    adapter = None

    def __init__(self, context, request, view, manager):
        super(TagIt, self).__init__(context, request, view, manager)
        registry = getUtility(IRegistry)
        try:
            settings = registry.forInterface(IPersonalTagsSettings)
        except:
            print "Error loading settings for personal tags"
            return
        self.adapter = getAdapter(self.context, ITagManager, name=settings.storage)

    def contextURL(self):
        return self.context.absolute_url()

    @property
    def available(self):
        if self.adapter is None:
            return False
        return self.adapter.editorAvailable()

class TagItManager(grok.ViewletManager):
    """
        If you want to place the viewlet in-situ, you can use this manager:

        <div tal:replace="structure provider:collective.personaltags.tagManager" />
    """
    grok.name('collective.personaltags.tagManager')
    grok.context(Interface)

