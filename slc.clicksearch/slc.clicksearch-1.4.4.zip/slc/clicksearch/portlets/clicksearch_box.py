from slc.clicksearch.util import make_link, current_query
import logging
from App.config import getConfiguration

from plone.app.portlets.portlets import base

from plone.portlets.interfaces import IPortletDataProvider

from plone.memoize.compress import xhtml_compress

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.clicksearch import ClickSearchMessageFactory as _

from zope import schema
from zope.schema.interfaces import ValidationError, WrongType

from zope.app.form import CustomWidgetFactory
from zope.app.form.browser import ObjectWidget
from zope.app.form.browser import ListSequenceWidget

from zope.component import queryMultiAdapter #@UnresolvedImport
from zope.formlib import form
from zope.interface import implements, Interface

from slc.clicksearch.config import BLACKLIST, WHITELIST

logger = logging.getLogger('slc.clicksearch.portlets.clicksearchbox')

class DisplayValuesInBlacklist(ValidationError):
    __doc__ = _("""There are display value(s) in this blacklist, please remove them.""")

class DisplayValuesNotInWhitelist(ValidationError):
    __doc__ = _("""There are display value(s) that do not occur in this whitelist, please add them.""")

class FilterList(schema.List):
    
    def _validate(self, value):
        """ Check that values in top and filter are mutually exclusive if filter
            is a blacklist or that top is a subset of filter if filter is a
            whitelist.

            The validation is not perfect. If there are two filter fields with the
            same value, we do not know which specific field we're dealing with.
        """
        if self._type is not None and not isinstance(value, self._type):
            raise WrongType(value, self._type)

        if hasattr(self.context, 'context'):
            request = self.context.context.request
            count = int(request.get('form.metadata.count', 0))
            for n in range(0, count):
                filter_type = request.get('form.metadata.%s.filter_type' % n)
                filter = request.get('form.metadata.%s.filter' % n, '').split()
                if filter == value:
                    top = request.get('form.metadata.%s.top' % n, '').split()
                    if filter_type == BLACKLIST:
                        if [i for i in top if i in filter]:
                            raise DisplayValuesInBlacklist(value)
                            
                    elif filter_type == WHITELIST:
                        if [i for i in top if i not in filter]:
                            raise DisplayValuesNotInWhitelist(value)


class IMetadataConfig(Interface):
    """ Storage class for metadata definitions """
    index = schema.Choice(title=_(u"Index"), 
                          vocabulary="slc.clicksearch.FilteredIndexVocabulary")
    title = schema.TextLine(title=(u"Title"), 
                            description=_(u"The readable title which will be \
                                            displayed in the portlet"))

    top = schema.List(title=_(u"Top entries for immediate display"),
                    description=_(u"In the case of dropdown widgets, such as \
                    used for 'Country' and 'Language', these entries will be \
                    ignored and can be left blank"),
                    required=False, default=[],
                    value_type = schema.TextLine(title=u"Filter"))

    filter_type = schema.Choice(title=_(u"Filter entries visible on the 'see more' page"),
                                values=[BLACKLIST, WHITELIST])
    filter = FilterList(required=False, default=[],
                        value_type = schema.TextLine(title=u"Filter"))


class MetadataConfig:
    implements(IMetadataConfig)
    
    def __init__(self, index=None, title='', top=[], filter_type=BLACKLIST, filter=[]):
        self.index = index
        self.title = title
        self.top = top
        self.filter_type = filter_type
        self.filter = []

class IClickSearchPortlet(IPortletDataProvider):
    """A portlet which shows metadata to restrict a search
    """

    header = schema.TextLine(title=_(u"Portlet header"),
                             description=_(u"Title of the rendered portlet"),
                             required=True)

    metadata = schema.List(title=_(u"Metadata"),
                           description=_(u"Select the Metadata to show in the filter"),
                           required=False,
                           value_type=schema.Object(IMetadataConfig, title=u"Search metadata"),
                           )
                      
class Assignment(base.Assignment):
    """
    Portlet assignment.    
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IClickSearchPortlet)

    header = u""
    metadata=[]

    def __init__(self, header=u"", metadata=[]):
        self.header = header
        self.metadata = metadata

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        return self.header

class Renderer(base.Renderer):
    """Portlet renderer.
    
    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    _template = ViewPageTemplateFile('clicksearch_box.pt')

    def __init__(self, context, request, view, manager, data):
        for metadata in data.metadata:
            if isinstance(metadata.top, basestring):
                metadata.top = metadata.top.split()
            if isinstance(metadata.filter, basestring):
                metadata.filter = metadata.filter.split()
        super(Renderer, self).__init__(context, request, view, manager, data)
        portal_languages = getToolByName(self.context, 'portal_languages')
        self.preflang = portal_languages.getPreferredLanguage()
        self.query = current_query(self.request)
        
        self.boxes = []
        self.boxmap = {}
        for i in self.data.metadata:
            index = i.index
            values = []
            if i.top:
                top = filter(lambda x:x, i.top)
                for elem in top:
                    link = make_link(self.request, index, elem)
                    values.append(dict(title=elem, link=link))

            self.boxes.append(dict(index=index, entries=values, title=i.title))
            self.boxmap[index] = (i.title, values)

    def _render_cachekey(method, self): #@NoSelf
        """ """
        preflang = getToolByName(self.context, 'portal_languages').getPreferredLanguage()
        portal_membership = getToolByName(self.context, 'portal_membership')
        member = portal_membership.getAuthenticatedMember()
        roles = member.getRolesInContext(self.context)
        modified = self.document() and self.document().modified or ''
        return (modified, roles, preflang)

    # Check if zope is not in debug_mode before caching
    def render(self):
        return xhtml_compress(self._template())

    config = getConfiguration()
    if not config.debug_mode:
        #render = ram.cache(_render_cachekey)
        # The render_cachekey contains a strange reference to self.document
        # Also the portlet works in debug mode but not in production. 
        # Assuming this is the problem. So we will not cache the portlet for now
        pass

    def title(self):
        return self.data.header

    def generate_hidden_fields(self):
        out = []
        for q in self.query.keys():
            if q=='SearchableText':
                continue
            out.append("""<input type="hidden" name="%s" value="%s">""" % (q, self.query[q]) )
        return "".join(out)
        
    def displayWidget(self, index):
        """ Fetches a specific view for the given metadata id or falls back to
            slc.clicksearch.generic
        """
        name = "slc.clicksearch.%s" % index
        logger.info("Name to lookup: %s" % name)
        
        view = queryMultiAdapter((self.context, self.request), name=name)
        if view is None:
            view = queryMultiAdapter((self.context, self.request), 
                                      name='slc.clicksearch.generic')

        return view(index=index, box_config=self.boxmap[index])

    def showReset(self):
        return (len(self.data.metadata) > 1 and self.request.QUERY_STRING) or \
            self.request.get('SearchableText', '')
        
class MetadataListWidget(ListSequenceWidget):
    """ Override the 'widgets' method from ListSequenceWidget, there is a bug
        that causes request form values to be lost when validation fails for any
        of the IMetadataConfig objects in the list.
    """

    def widgets(self):
        """Return a list of widgets to display"""
        sequence = self._getRenderedValue()
        result = []
        for i, value in enumerate(sequence):
            widget = self._getWidget(i)
            # XXX: local fix
            if value is not None:
                widget.setRenderedValue(value)
            result.append(widget)
        return result
        
metadata_obj_widget = CustomWidgetFactory(ObjectWidget, MetadataConfig)
metadata_widget = CustomWidgetFactory(MetadataListWidget,
                                      subwidget=metadata_obj_widget)
               
        
class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IClickSearchPortlet)
    form_fields['metadata'].custom_widget = metadata_widget
    
    label = _(u"Add Clicksearch Portlet")
    description = _(u"This portlet displays metadata to search for.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IClickSearchPortlet)
    form_fields['metadata'].custom_widget = metadata_widget

    label = _(u"Edit Clicksearch Portlet")
    description = _(u"This portlet displays metadata to search for.")


