from slc.clicksearch.util import current_query, make_qs
import logging
from time import time

from zope.component import getMultiAdapter, queryMultiAdapter, getUtility #@UnresolvedImport
from Products.CMFPlone import PloneMessageFactory as _
from plone.memoize import ram
from plone.portlets.interfaces import IPortletManager, IPortletAssignmentMapping

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.clicksearch.config import BLACKLIST, WHITELIST, SAFE_INDEXES

logger = logging.getLogger("slc.clicksearch")


class DetailsView(BrowserView):
    """ The details view"""
    template = ViewPageTemplateFile('templates/details.pt')

    def __call__(self):
        query = current_query(self.request)
        self.index = query['selected_index']
        del query['selected_index']
        del query['index_title']
        self.query = query

        return self.template()

    def display_values(self):
        """ Displays the values from the index """
        cat = getToolByName(self.context, 'portal_catalog')
        idx = cat._catalog.getIndex(self.index)
        name = "slc.clicksearch.index_%s" % self.index
        view = queryMultiAdapter((idx, self.request), name=name)
        if view is None:
            view = getMultiAdapter((idx, self.request), name='default_view')

        context = self.context
        metadata = []

        for name in [u'plone.leftcolumn', u'plone.rightcolumn']:
            manager = getUtility(IPortletManager, name=name)
            column = getMultiAdapter((context, manager), IPortletAssignmentMapping)

            for v in column.values():
                if hasattr(v, 'metadata'):
                    metadata += [m for m in v.metadata if m.index == self.index]

        blacklist = []
        whitelist = []

        for m in metadata:
            # transitional check, should not be necessary anmore.
            if m.filter is None:
                m.filter = []
                
            if m.filter_type == BLACKLIST:
                blacklist += m.filter
            elif m.filter_type == WHITELIST:
                whitelist += m.filter

        external_q = self.context.buildQuery()
        path = '/'.join(self.context.getPhysicalPath())
        return view(query=self.query, blacklist=blacklist, whitelist=whitelist,
            additional_query=external_q, path=path)

    
class DefaultIndexView(BrowserView):
    """ Basic functionality, lists uniqueValuesFor Index """

    template = ViewPageTemplateFile('templates/default_index.pt')

    def __call__(self, query, blacklist=[], whitelist=[], additional_query=None, path=None):     
        values = self.context.uniqueValues()
        if whitelist:
            filtered_values = [str(v) for v in values if v not in blacklist and v in whitelist]
        else:
            filtered_values = [str(v) for v in values if v not in blacklist]

        self.uniqueValues = filtered_values
        self.query = query
        self.additional_query = additional_query
        self.path = path
        self.valueSet = [dict(id=value, title=self.prepare_title(value), link=self.select_link(value)) for value in filtered_values]
        return self.template()

    def select_link(self, value):
        query = self.query
        query[self.context.id] = value
        new_qs = make_qs(query)
        return "clicksearch?%s" % new_qs

    def prepare_title(self, id):
        """ use some processing to find a human readable title for the given metadata element id
            like Musculoskeletal disorders for msd
            override in subclass
        """
        return _(id)

    def _render_cachekey(method, self): #@NoSelf
        return (modified, roles, preflang)

    # needs to be cached aggressively
    def calc_num_results_cachekey(method, self): #@NoSelf
        period = time() // (60 * 60)
        return (period, self.query, self.path)

    @ram.cache(calc_num_results_cachekey)
    def calc_num_results(self):
        """ this one needs to be cached aggressively as it executes a query for every value.
            This may be a showstopper for large indexes. Therefore we add a hard limit for now.
        """
        if len(self.uniqueValues) > 20 and \
            (self.context.id not in SAFE_INDEXES and len(self.uniqueValues) > 50):
            return {}
        query = self.query
        if self.additional_query:
            query.update(self.additional_query)
        cat = getToolByName(self.context, 'portal_catalog')
        nums = {}
        logger.info(query)
        for val in self.uniqueValues:
            query[self.context.id] = val
            results = cat(query)
            nums[val] = len(results)
            del results
        logger.info("executing calc_num_results: %s" % str(nums))
        return nums

class ATVMTreeIndexView(DefaultIndexView):
    """ Tree functionality, uses an atvocabularymanager tree vocabulary
        uses jquery to display the tree"""

    template = ViewPageTemplateFile('templates/atvm_tree_index.pt')
    vocabulary_name = None   # specify the name of the vocabulary inside atvm

    def __call__(self, query, blacklist=[], whitelist=[]):
        # XXX: black/whitelisting to be implemented
        atvm = getToolByName(self.context, 'portal_vocabularies')
        self.vocabulary = getattr(atvm, self.vocabulary_name, None)
        self.query = query
        return self.template()

    def get_terms(self):
        return self.vocabulary.getVocabularyDict(self.vocabulary)

