from pprint import pformat
from Products.CMFCore.utils import getToolByName
from zope.interface import Interface, Attribute
from AccessControl import Unauthorized
from Acquisition import Implicit
from OFS.SimpleItem import Item
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.component import getUtility
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Acquisition import aq_inner
from zope.interface import implements
from zope.component import getMultiAdapter
from Products.Five import BrowserView
from plone.memoize import view
import re
from zope.traversing.interfaces import ITraversable
from Products.Archetypes.utils import OrderedDict
from Products.CMFCore.permissions import ModifyPortalContent

from Products.CMFPlone.utils import safe_unicode
from zope.annotation import IAnnotations
from collective.annotationbrowser.utils import custom_repr
from collective.annotationbrowser.browser.interfaces import IAnnotationBrowserView

VALUE_MAX_LENGTH = 150

_marker = object()

class AnnotationBrowserView(BrowserView):
    implements(IAnnotationBrowserView)

    @view.memoize_contextless
    def tools(self):
        """ returns tools view. Available items are all portal_xxxxx 
            For example: catalog, membership, url
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/tools.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_tools")

    @view.memoize_contextless
    def portal_state(self):
        """ returns 
            http://dev.plone.org/plone/browser/plone.app.layout/trunk/plone/app/layout/globals/portal.py
        """
        return getMultiAdapter((self.context, self.request), name=u"plone_portal_state")

    @view.memoize
    def annotations(self):
        context = aq_inner(self.context)
        return IAnnotations(context)
        
    def num_blacklisted(self):
        ann = self.annotations()
        portal = getUtility(IPloneSiteRoot)
        blacklist = portal.getProperty('annotationbrowser.blacklist', [])
        count = 0
        for key in ann.keys():
            for bl in blacklist:
                if re.match(bl, key) is not None:
                    count += 1
                    break
        return count

    def delete_key(self, keyname):
        """ Remove annotation key from the storage. 
            MAY BE DANGEROUS 
        """
        ann = self.annotations()
        ptool = getToolByName(self.context, 'plone_utils')
        if ann.has_key(keyname):
            del ann[keyname]
            ptool.addPortalMessage('Key %s removed' % keyname)
        self.request.response.redirect(self.context.absolute_url() + '/ann_view')

    def ann_keys(self):
        ann = self.annotations()
        result = list()
        portal = getUtility(IPloneSiteRoot)
        blacklist = portal.getProperty('annbrowser.blacklist', [])
        whitelist = portal.getProperty('annbrowser.whitelist', [])
        if not whitelist:
            whitelist = ['.*',] 
                
        # process blacklist
        for key in ann.keys():
            passed = False
            for wl in whitelist:
                if re.match(wl, key) is not None:
                    passed = True
                    break
            for bl in blacklist:
                if re.match(bl, key) is not None:
                    passed = False
                    break
            if passed:
                result.append(key)
        return result

    def ann_dict(self):
        ann = self.annotations()
        result = OrderedDict()
        for key in sorted(self.ann_keys()):
            is_editable = False
            typ = 'unknown'
            value = ann.get(key, _marker)
            if value is _marker:
                value = 'N/A'
            else:
                if isinstance(value, basestring):
                    typ = 'string'
                    is_editable = True
                elif isinstance(value, int):
                    typ = 'int'
                    is_editable = True
                elif isinstance(value, float):
                    typ = 'float'
                    is_editable = True
            value = custom_repr(value)
            result[key] = dict(value = safe_unicode(value)[:VALUE_MAX_LENGTH], 
                               editable=is_editable, 
                               typ=typ)
        return result

class AnnotationBrowserEdit(BrowserView):
    
    def processForm(self):
        context = aq_inner(self.context)
        if (self.request.form.get('form.submitted', '') == '1') and self.request.form.has_key('submit'):
            ann = IAnnotations(context)
            for k, v  in self.request.form.items():
                if ann.has_key(k):
                    ann[k] = v
        self.request.response.redirect(context.absolute_url() + '/ann_view')
        
class IAnnotationContent(Interface):
    content = Attribute(u"returns the content of the annotation storage")


class AnnotationContent(Implicit, Item):
    """
           Code inspired by archetypes.fieldtraverser
    """ 

    implements(IAnnotationContent, IBrowserPublisher)

    def __init__(self, context, request, name, value):
        self.context = context
        self.request = request
        self.name = name
        self.value = value

    def browserDefault(self, request):
        return self, ('@@view',)

    @property
    def content(self):

        # if not self.field.checkPermission('r', self.context):
        #     raise Unauthorized, \
        #           'Your not allowed to access the requested field %s.' % \
        #           self.field.getName()
        # 

        mtool = getToolByName(self.context, 'portal_membership')
        if not mtool.checkPermission(ModifyPortalContent, self.context):
            raise Unauthorized, \
                  'Your not allowed to access the requested resource %s.' % \
                  self.name
            
        return pformat(self.value)
        


class AnnotationContentView(BrowserView):
    """
           Code inspired by archetypes.fieldtraverser
    """ 
    
    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return self.context.content
        
class AnnotationTraverser(object):
    """Used to traverse to content stored in IAnnotations
       Code inspired by archetypes.fieldtraverser
       
    """
    implements(ITraversable)

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, ignore):
        ann = IAnnotations(self.context)
        value = ann.get(name, '')
        return AnnotationContent(self.context, self.request, name, value).__of__(self.context)

