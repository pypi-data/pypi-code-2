from Acquisition import aq_inner

from zope.interface import implements
from zope import schema
from zope.formlib import form

from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.app.portlets.portlets import base
from plone.app.portlets.portlets.recent import (
        Renderer as BaseRenderer, Assignment as BaseAssignment, IRecentPortlet)

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.portlet.customizablerecent import CustomizableRecentMessageFactory as _
from zope.i18nmessageid.message import MessageFactory
PMF = MessageFactory('plone')

class ICustomizableRecent(IRecentPortlet):
    """Customizable Recent portlet inherits from Plone Recent Portlet
    """

    name = schema.TextLine(
            title=PMF(u"label_recent_title", default=u"Title"),
            description=_(u"help_recent_title",
                          default=u"The title of the recent items portlet. "
                                    "Leave blank if you want it to be computed by default as "
                                    "Recent items, or Recent items in ... if root node has been set."),
            default=u"",
            required=False)

    content_types = schema.Tuple(title=PMF(u"Content type"),
                             description=_(u"The content types to display."),
                             required=False,
                             value_type=schema.Choice(vocabulary="plone.app.vocabularies.ReallyUserFriendlyTypes"))

    root = schema.Choice(
            title=PMF(u"label_navigation_root_path", default=u"Root node"),
            description=_(u'help_recent_root',
                          default=u"You may search for and choose a folder "
                                    "to act as the root of the recent elements displayed. "
                                    "Leave blank to use the Plone site root."),
            required=False,
            source=SearchableTextSourceBinder({'is_folderish' : True},
                                              default_query='path:'))
    long_time_format = schema.Bool(
                 title=_(u"Display the date in long format"),
                 description=_(u"Display the date of the last modification in dd/mm/yyyy hh:mm format"),
                 default=False,
                 required=True)

class Assignment(BaseAssignment):
    """Portlet assignment.
    """

    implements(ICustomizableRecent)

    title = PMF("Customizable recent elements")

    def __init__(self, **kwargs):
        self.content_types = kwargs.pop('content_types', ())
        self.root = kwargs.pop('root', '')
        self.name = kwargs.pop('name', u"")
        self.long_time_format = kwargs.pop('long_time_format','')
        super(Assignment, self).__init__(**kwargs)


class Renderer(BaseRenderer):
    """Portlet renderer.
    """

    _template = ViewPageTemplateFile('recent.pt')

    def recently_modified_link(self):
        url = '%s/recently_modified' % self.navigation_root_url
        if self.data.content_types:
            query = "&".join(["portal_type:list=%s" % ptype for ptype in self.data.content_types])
            url = "%s?%s" % (url, query)

        return url

    @memoize
    def _data(self):
        query = {'sort_limit': self.data.count,
                 'sort_on': 'modified',
                 'sort_order': 'reverse',
                 'portal_type': self.data.content_types or self.typesToShow,
                 'path': self.navigation_root_path + (self.data.root or '')
                 }
        return self.catalog(**query)[:self.data.count]

    @property
    def long_format(self):
        return getattr(self.data, 'long_time_format', False)

    @property
    def title(self):
        if self.data.name:
            return self.data.name
        elif self.data.root:
            root = self.context.restrictedTraverse(self.navigation_root_path + self.data.root)
            return _('local_recent_label', default=u"Recent items in ${name}",
                     mapping={'name': root.title_or_id().decode('utf-8')})
        else:
            return PMF('box_recent_changes', default=u"Recent Changes")


class AddForm(base.AddForm):
    """Portlet add form.
    """
    form_fields = form.Fields(ICustomizableRecent)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    """
    form_fields = form.Fields(ICustomizableRecent)
