from zope import interface
from zope import component
from zope import schema

from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName

from interfaces import IInternalLink
from interfaces import IExternalLink
from interfaces import ILink

import utils

from collective.formlib.link import MessageFactory as _

class InternalLink(object):
    """An implementation of an internal link that uses UID for weak
    referencing."""
    
    interface.implements(IInternalLink)

    def __init__(self, reference, title, description):
        self.reference = reference
        self.title = title
        self.description = description
        
    def __repr__(self):
        return u"<InternalLink %s>" % self.reference

    def __unicode__(self):
        brain = self._brain()

        if brain is None:
            return u""

        path = "/" + brain.getPath().lstrip('/')
        return utils.pack(path, self.title, self.description)

    def _brain(self):
        site = getSite()
        catalog = getToolByName(site, 'uid_catalog')
        brains = catalog(UID=self.reference)

        if brains:
            return brains[0]

        return None
    
    def pretty_title_or_uri(self):
        if self.title:
            return self.title

        brain = self._brain()

        if brain is None:
            return _(u"Broken link")

        return brain.Title or brain.id
    
    def absolute_url(self):
        brain = self._brain()

        if brain is None:
            return '#'

        site = getSite()

        return site.absolute_url() + brain.getURL(site)
    
class ExternalLink(object):
    interface.implements(IExternalLink)

    def __init__(self, uri, title, description):
        self.uri = uri
        self.title = title
        self.description = description
        
    def __repr__(self):
        return u"<ExternalLink %s>" % self.uri

    def __unicode__(self):
        return utils.pack(self.uri, self.title, self.description)

    def pretty_title_or_uri(self):
        if self.title:
            return self.title

        uri = self.uri
        return uri[uri.find('//')+2:]

    def absolute_url(self):
        return self.uri
    
class Link(schema.TextLine):
    """
      >>> link = Link()

    We need to set up a mock context that implements internal link resolving.
    
       >>> class MockContext(object):
       ...     __parent__ = portal_url = uid_catalog = property(
       ...         lambda self: MockContext())
       ...
       ...     def getPortalObject(self):
       ...         return self
       ...
       ...     def restrictedTraverse(self, path):
       ...         self.path = path
       ...         return self
       ...
       ...     def UID(self):
       ...         return "Mock UID resolved for %s" % self.path
       ...
       ...     def getSiteManager(self):
       ...         return self
       
       >>> link.context = MockContext()
       
       >>> from zope.app.component.hooks import setHooks, setSite
       >>> setHooks()
       >>> setSite(link.context)
       
    Only URIs that provide a protocol are parsed as external links.
    
      >>> link.fromUnicode(
      ...     '"Plone":http://www.plone.org:"An open-source content management system."')
      <ExternalLink http://www.plone.org>

    An URI like www.plone.org will thus be interpreted as an internal link.
    
      >>> link.fromUnicode(
      ...     '"Plone":www.plone.org:"An open-source content management system."')
      <InternalLink Mock UID resolved for www.plone.org>

    Finally, two examples of something that actually looks like
    internal links, just to be clear.

       >>> link.fromUnicode(
       ...     '"Fruit and greens":fruits-and-greens:"Eat well, live long."')
       <InternalLink Mock UID resolved for fruits-and-greens>
    
       >>> link.fromUnicode(
       ...     '"Fruit and greens":/shop/fruits-and-greens:"Eat well, live long."')
       <InternalLink Mock UID resolved for shop/fruits-and-greens>
    """

    def fromUnicode(self, u):
        uri, title, description = utils.unpack(u)

        m = utils.uri.match(uri)
        if m is not None and m.group('protocol'):
            return ExternalLink(uri, title, description)
        else:
            # resolve object
            path = str(uri)
            
            try:
                portal = getSite()
                context = getattr(self.context, '__parent__', portal)
                if path.startswith('/'):
                    item = portal.restrictedTraverse(path[1:])
                else:
                    item = context.restrictedTraverse(path)

                reference = item.UID()
                
            except KeyError:
                reference = None

            return InternalLink(reference, title, description)

    def _validate(self, value):
        return ILink.providedBy(value)
