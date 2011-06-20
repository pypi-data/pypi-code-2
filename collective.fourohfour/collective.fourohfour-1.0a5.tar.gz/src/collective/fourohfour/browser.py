from paste.httpexceptions import HTTPMovedPermanently

from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button

from urllib import unquote

from zope.interface import Interface
from zope.component import queryUtility, getMultiAdapter

from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName

from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.redirector.interfaces import IRedirectionPolicy

from plone.registry.interfaces import IRegistry

from plone.memoize.instance import memoize
from Products.CMFPlone.interfaces.siteroot import IPloneSiteRoot
from Products.statusmessages.interfaces import IStatusMessage

import logging

logger = logging.getLogger('plone.app.redirector')

from collective.fourohfour import MessageFactory as _
from collective.fourohfour.interfaces import IFourOhFourSettings
from collective.fourohfour.interfaces import IBrowserLayer

class FourOhFour(grok.View):
    grok.context(Interface)
    grok.name("404-error")
    grok.layer(IBrowserLayer)
    # note: view is public
    
    display_suggestions = True
    
    def update(self):
        
        # Try the redirect first and abort if we redirected
        location = self.attempt_redirect()
        if location:
            self.request.response.redirect(location, status=302, lock=1)
            # raise HTTPMovedPermanently(location)
        
        # Determine if we should display suggestions
        
        self.display_suggestions = True
        registry = queryUtility(IRegistry)
        if registry is not None:
            self.display_suggestions = registry.forInterface(IFourOhFourSettings).displaySuggestions
        
        self.request.set('disable_border', True)
    
    def attempt_redirect(self):
        
        storage = queryUtility(IRedirectionStorage)
        if storage is None:
            return None
        
        # Attempt a redirect based on a path with a query string
        old_path_qs = self.request.environ.get('collective.fourohfour.original_path_qs', None)
        
        if old_path_qs:
            new_path = storage.get(old_path_qs)
        
            if new_path:
                return self.request.physicalPathToURL(new_path)
        
        # Next, try the path without the query string
        old_path = self.request.environ.get('collective.fourohfour.original_path', None)
        if old_path and old_path != old_path_qs:
            new_path = storage.get(old_path)
        
            if new_path:
                return self.request.physicalPathToURL(new_path)
        
        # Otherwise, try a more standard query that takes virtual hosting into account
        
        url = self._url()
        if not url:
            return None

        try:
            old_path_elements = self.request.physicalPathFromURL(url)
        except ValueError:
            return None

        old_path = '/'.join(old_path_elements)
        new_path = storage.get(old_path)

        if not new_path:

            # If the last part of the URL was a template name, say, look for
            # the parent

            if len(old_path_elements) > 1:
                old_path_parent = '/'.join(old_path_elements[:-1])
                template_id = unquote(url.split('/')[-1])
                new_path_parent = storage.get(old_path_parent)
                if new_path_parent == old_path_parent:
                    logger.warning("source and target are equal : [%s]"
                         % new_path_parent)
                    logger.warning("for more info, see "
                        "https://dev.plone.org/plone/ticket/8840")
                if new_path_parent and new_path_parent <> old_path_parent:
                    new_path = new_path_parent + '/' + template_id

        if not new_path:
            return None

        return self.request.physicalPathToURL(new_path)

    def find_first_parent(self):
        path_elements = self._path_elements()
        if not path_elements:
            return None
        portal_state = getMultiAdapter((aq_inner(self.context), self.request),
             name='plone_portal_state')
        portal = portal_state.portal()
        for i in range(len(path_elements)-1, 0, -1):
            obj = portal.restrictedTraverse('/'.join(path_elements[:i]), None)
            if obj is not None:
                return obj
        return None

    def search_for_similar(self):
        path_elements = self._path_elements()
        if not path_elements:
            return None
        path_elements.reverse()
        policy = IRedirectionPolicy(self.context)
        ignore_ids = policy.ignore_ids
        portal_catalog = getToolByName(self.context, "portal_catalog")
        portal_state = getMultiAdapter((aq_inner(self.context), self.request),
             name='plone_portal_state')
        navroot = portal_state.navigation_root_path()
        for element in path_elements:
            # Prevent parens being interpreted
            element=element.replace('(', '"("')
            element=element.replace(')', '")"')
            if element not in ignore_ids:
                result_set = portal_catalog(SearchableText=element,
                    path = navroot,
                    portal_type=portal_state.friendly_types(),
                    sort_limit=10)
                if result_set:
                    return result_set[:10]
        return []

    @memoize
    def _url(self):
        """Get the current, canonical URL
        """
        return self.request.environ.get('collective.fourohfour.original_url',
                 self.request.get('ACTUAL_URL',
                   self.request.get('VIRTUAL_URL',
                     self.request.get('URL',
                       None))))

    @memoize
    def _path_elements(self):
        """Get the path to the object implied by the current URL, as a list
        of elements. Get None if it can't be calculated or it is not under
        the current portal path.
        """
        url = self._url()
        if not url:
            return None

        try:
            path = '/'.join(self.request.physicalPathFromURL(url))
        except ValueError:
            return None

        portal_state = getMultiAdapter((aq_inner(self.context), self.request),
            name='plone_portal_state')
        portal_path = '/'.join(portal_state.portal().getPhysicalPath())
        if not path.startswith(portal_path):
            return None

        return path.split('/')

def validateData(value):
    entries = value.splitlines()
    aliases = {}
    
    invalid = []
    
    for entry in entries:
        if "=>" not in entry:
            invalid.append(entry)
            continue
        
        source, target = entry.split('=>')
        source = source.strip()
        target = target.strip()
        
        if "://" in source or "://" in target or not source.startswith('/') or not target.startswith('/'):
            invalid.append(entry)
            continue
        
        aliases[source] = target
    
    return len(invalid) == 0 

class IBulkLoad(form.Schema):
    
    prependPathSource = schema.Bool(
            title=_(u"Prepend portal root path to the alias source"),
            description=_(u"Enable this if you are using path based virtual hosting with repoze.vhm#vhm_path "
                           "or a standard VirtualHostMonster."),
            default=True,
        )
    
    prependPathTarget = schema.Bool(
            title=_(u"Prepend portal root path to the alias target"),
            description=_(u"You almost certainly want to enable this."),
            default=True,
        )
    
    data = schema.ASCII(
            title=_(u"Bulk load data"),
            description=_("Paste a set of aliases in the form /old-path => /new_path, one per line."),
            constraint=validateData,
        )    
    
class BulkLoad(form.SchemaForm):
    grok.name("bulk-load-aliases")
    grok.context(IPloneSiteRoot)
    grok.require("cmf.ManagePortal")
    grok.layer(IBrowserLayer)
    
    label = _(u"Bulk load aliases")
    
    schema = IBulkLoad
    ignoreContext = True
    
    def updateWidgets(self):
        super(BulkLoad, self).updateWidgets()
        self.widgets['data'].rows = 40
    
    @button.buttonAndHandler(u'Import')
    def handleImport(self, action):
        data, errors = self.extractData()
        
        portal_state = getMultiAdapter((aq_inner(self.context), self.request), name='plone_portal_state')
        portal_path = '/'.join(portal_state.portal().getPhysicalPath())
        
        if not errors:
            entries = data['data'].splitlines()
            aliases = {}
            
            prependSource = data['prependPathSource']
            prependTarget = data['prependPathTarget']
            
            storage = queryUtility(IRedirectionStorage)
            if storage is None:
                raise KeyError("Cannot find redirection storage")
            
            for entry in entries:
                source, target = entry.split('=>')
                source = source.strip()
                target = target.strip()
                
                if prependSource and not source.startswith(portal_path):
                    source = "%s%s" % (portal_path, source)
                
                if prependTarget and not target.startswith(portal_path):
                    target = "%s%s" % (portal_path, target)
                
                storage.add(source, target)
            
            self.status = _(u"Import complete")
            
