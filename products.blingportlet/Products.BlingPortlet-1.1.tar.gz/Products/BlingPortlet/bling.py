import datetime
import random
import time
from copy import deepcopy
try:
    from hashlib import md5
except:
    from md5 import md5
from random import randint

from Acquisition import aq_inner
from Products.ATContentTypes.interface.image import IATImage
from Products.ATContentTypes.interface.news import IATNewsItem
from Products.BlingPortlet import BlingPortletMessageFactory as _
from Products.BlingPortlet.interfaces import IBlingPortlet, IBlingImage, IBlingSlideshowPortlet, IBlingable
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.app.portlets.portlets import base
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements


class BaseAssignment(base.Assignment):
    implements(IBlingPortlet)

    name = u''
    source = None
    base_title = u'Base Bling Portlet'
    def __init__(self, name, source, scale, links):
        self.name = name
        self.source = source
        self.links = links
        self.scale = scale

    @property
    def title(self):
        return self.name or self.base_title

class Assignment(BaseAssignment):
    base_title = u'Bling Portlet'
    def __init__(self, name, source, scale, links, change):
        BaseAssignment.__init__(self, name, source, scale, links)
        self.change = change
    
class SlideshowAssignment(BaseAssignment):
    base_title = u'Bling Slideshow'
    implements(IBlingSlideshowPortlet)
    
    def __init__(self, name, source, scale, links, interval, ordering, repeat, desc_limit):
        BaseAssignment.__init__(self, name, source, scale, links)
        self.interval = interval
        self.ordering = ordering
        self.repeat = repeat
        self.desc_limit = desc_limit

class BaseRenderer(base.Renderer):
    # only find adaptable objects which are accessible to all
    base_query = { 'object_provides' : (IATNewsItem.__identifier__,
                                        IATImage.__identifier__,
                                        IBlingable.__identifier__),
                   'allowedRolesAndUsers' : ('Anonymous',),
    }
        
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        self.portal_root = portal_state.navigation_root_path()
        
        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()

    def title(self):
        return self.data.name

    def render(self):
        return self._template()
    
    def links(self): 
        return self.data.links 
    
    def scale(self): 
        return self.data.scale 
        
    
class Renderer(BaseRenderer):
    _template = ViewPageTemplateFile('bling.pt')
     
    def getResultsIndex(self, resultsLength):
        if self.data.change == u'Random':
            return randint(0,resultsLength-1)
        elif self.data.change == u'Each second':
            return int(time.time()) % resultsLength
        elif self.data.change == u'Each minute':
            return int(time.time()) / 60 % resultsLength
        elif self.data.change == u'Each hour':
            return int(time.time()) / 3600 % resultsLength
        elif self.data.change == u'Each day':
            return int(time.time()) / 86400 % resultsLength
        elif self.data.change == u'Each week':
            return int(time.time()) / 604800 % resultsLength
        elif self.data.change == u'Each month':
            now = datetime.datetime.now()
            return (now.month + now.year*12) % resultsLength
        elif self.data.change == u'Each year':
            now = datetime.datetime.now()
            return now.year % resultsLength
        return 0

    def getdata(self):
        query = deepcopy(self.base_query)
        query['path'] = { 'query': self.portal_root + self.data.source, 'depth': 1 }
        results = self.catalog.unrestrictedSearchResults(query)
        if not len(results):
            return None
        
        return IBlingImage(results[self.getResultsIndex(len(results))].getObject(), None)
    
class SlideshowRenderer(BaseRenderer):
    _template = ViewPageTemplateFile('slideshow.pt')

    def portlethash(self):
        concat_txt = "%s\n%s" % (self.manager.__name__, self.data.__name__)
        return md5(concat_txt).hexdigest()
        
    def interval(self):
        return self.data.interval
        
    def ordering(self):
        return self.data.ordering
        
    def repeat(self):
        return self.data.repeat
    
    def desc_limit(self):
        return self.data.desc_limit
    
    def getdata(self):
        query = deepcopy(self.base_query)
        query['path'] = { 'query': self.portal_root + self.data.source, 'depth': 1 }
        
        if self.data.ordering == u'Sequential':
            query['sort_on'] = 'getObjPositionInParent'
            query['sort_order'] = 'ascending'
            
        results = self.catalog.unrestrictedSearchResults(query)
        filtered_results = [IBlingImage(r.getObject(), None) for r in results if r is not None]
        
        if self.data.ordering == u'Random':
            random.shuffle(filtered_results)
        
        return filtered_results

class AddForm(base.AddForm):
    form_fields = form.Fields(IBlingPortlet)
    form_fields['source'].custom_widget = UberSelectionWidget
    label = _(u"Add Bling Portlet")
    description = _(u"This portlet displays bling.")

    def create(self, data):
        return Assignment(**data)
    
class SlideshowAddForm(base.AddForm):
    form_fields = form.Fields(IBlingSlideshowPortlet)
    form_fields['source'].custom_widget = UberSelectionWidget
    label = _(u"Add Bling Slideshow Portlet")
    description = _(u"This portlet displays animated bling.")

    def create(self, data):
        return SlideshowAssignment(**data)
    

class EditForm(base.EditForm):
    form_fields = form.Fields(IBlingPortlet)
    form_fields['source'].custom_widget = UberSelectionWidget
    label = _(u"Edit Bling Portlet")
    description = _(u"This portlet displays bling.")    

class SlideshowEditForm(base.EditForm):
    form_fields = form.Fields(IBlingSlideshowPortlet)
    form_fields['source'].custom_widget = UberSelectionWidget
    label = _(u"Edit Bling Slideshow Portlet")
    description = _(u"This portlet displays animated bling.")    
