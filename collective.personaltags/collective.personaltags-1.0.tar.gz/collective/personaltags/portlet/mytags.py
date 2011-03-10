
from zope.component import getAdapter, getUtility

from zope.interface import implements
from zope import schema
from zope.formlib import form

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.registry.interfaces import IRegistry

from ..interfaces import ITagManager, IPersonalTagsSettings

class IMyTagsPortlet(IPortletDataProvider):
    """There is really no class - just a lot of classes configured together"""
    count = schema.Int(title=u'Number of tags to display',
        required=True, default=5)

class Assignment(base.Assignment):
    """This is a mandatory part - it doesn't do anything"""
    implements(IMyTagsPortlet)

    count = 5

    def __init__(self, count=5):
        self.count = count
        
    @property
    def title(self):
        return u"My Tags"

class AddForm(base.AddForm):
    """This is a mandatory part - it doesn't do anything"""
    form_fields = form.Fields(IMyTagsPortlet)
    label = u"Add MyTags Portlet"
    description = u"This portlet displays Tags for the current user."

    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    """This is a mandatory part - it doesn't do anything"""
    form_fields = form.Fields(IMyTagsPortlet)
    label = u"Edit MyTags Portlet"
    description = u"This portlet displays Tags for the current user."


class Renderer(base.Renderer):
    """Render the portlet"""
    _template = ViewPageTemplateFile('templates/mytags.pt')

    tags_for_current_user = None
    adapter = None

    viewurl = None
    settings = None
    adapter = None

    def __init__(self, context, request, view, manager, data):
        super(Renderer, self).__init__(context, request, view, manager, data)

        try:
            registry = getUtility(IRegistry)
            self.settings = settings = registry.forInterface(IPersonalTagsSettings)
        except:
            print "Error loading settings for personal tags"
            return

        try:
            self.adapter = getAdapter(self.context, ITagManager, name=settings.storage)
        except:
            print "Error loading adapter for : ", settings.storage
            return

        self.viewurl = settings.viewurl
        if not self.viewurl:
            self.viewurl = self.adapter.defaultViewName

    @property
    def user(self):
        return self.request.AUTHENTICATED_USER.getUserName()

    def tags_for_current_user(self):
        if not self.adapter:
            return []
        tags = self.adapter.getTagsAndCounts()
        if not tags:
            return []
        return tags[:self.data.count]

    def tags_for_current_user_below_fold(self):
        if not self.adapter:
            return []
        tags = self.adapter.getTagsAndCounts()
        if not tags or len(tags) < self.data.count:
            return []
        return tags[self.data.count:]

    def render(self):
        return self._template()

    @property
    def available(self):
        if self.adapter is None:
            return False
        return self.adapter.portletAvailable()
