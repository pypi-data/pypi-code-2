import os
import copy
import re
from time import time

from zope.interface import implements
from Products.CMFCore.utils import getToolByName

from quintagroup.portlet.cumulus.interfaces import ITagsRetriever
from quintagroup.portlet.cumulus.catalog import GlobalTags

from plone.memoize import ram

re_flags = re.S|re.U|re.M|re.X
NOT_SIMPLE_URL_RE = re.compile('%[(][^()]+[)]s', re_flags)

def _cachekey(method, self, path):
    """Time, language, settings and member based cache
    """
    membership = getToolByName(self.context, 'portal_membership')
    lang = self.context.REQUEST.get('LANGUAGE', 'en')
    memberid = membership.getAuthenticatedMember()
    return hash((lang, memberid, path, time() // self.data.refreshInterval))

class DummyData(object):
    path = None

class LocalTags(GlobalTags):
    implements(ITagsRetriever)

    def __init__(self, context):
        GlobalTags.__init__(self, context)
        self.portal = getToolByName(context, 'portal_url')
        self.data = DummyData()

    def getTags(self, number=None, data=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        if data:
            self.data = data
        cat = getToolByName(self.context, 'portal_catalog')
        index = cat._catalog.getIndex('Subject')
        tags = []
        if not self.data.path:
            tags = self.getGlobalTags(number)
        else:
            tags = self.getLocalTags(number)
        return tags


    def getPath(self, path):
        result = path
        ppath = self.portal.getPortalPath()
        if result.startswith('/'):
            if not result.startswith(ppath):
                result = ppath + result
        else:
            result = '/'.join(list(self.context.getPhysicalPath())+[result])
        return result

    @ram.cache(_cachekey)
    def getSubKeywords(self, path):
        cat = getToolByName(self.context, 'portal_catalog')
        brains = cat.searchResults(**{'path': path})
        tags = {}
        for brain in brains:
            for key in brain.Subject:
                if not key in tags:
                    tags[key] = 0
                tags[key] += 1
        return tags

    def getLocalTags(self, number=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        path = self.getPath(self.data.path)
        tags = self.getSubKeywords(path)
        res = []
        for name in tags:
            name = name.decode(self.default_charset)
            url = '%s/search?path=%s&Subject:list=%s' % (self.portal_url, path, name)
            res.append((name, tags[name], url))
        if number:
            if number >= res: number = res
            res = res[:number]
        return res


    def getGlobalTags(self, number=None):
        """ Entries of 'Categories' archetype field on content are assumed to be tags.
        """
        return GlobalTags.getTags(self, number)

class CustomLocalTags(LocalTags):

    def getLocalTags(self, number=None):
        """getLocalTags."""
        tags = LocalTags.getLocalTags(self, None)
        su = getattr(self.data, 'search_url', '')
        plone = self.portal.getPortalObject()
        common_vars = {'portal_url': plone.absolute_url(),
                       'portal_path': '/'.join(plone.getPhysicalPath()),
                       'here_url': self.context.absolute_url(),
                       'here_path': '/'.join(plone.getPhysicalPath()),
                      }
        if su:
            simple_url = not NOT_SIMPLE_URL_RE.match(su)
            for i, tag in enumerate(tags[:]):
                tag = list(tag)
                if simple_url:
                    tag[2] = os.path.join(su, tag[0])
                else:
                    v = copy.deepcopy(common_vars)
                    v.update({
                        'tag': tag[0],
                        'tag_weight': tag[1],
                    })
                    tag[2] = su % v
                path = self.getPath(self.data.path)
                # honour path restriction
                if path and (not 'path=' in tag[2]):
                    urlsep = '?'
                    if '?' in tag[2]: 
                        urlsep = '&'
                    tag[2] += '%spath=%s' % (urlsep, path)
                tags[i] = tag
        return tags


