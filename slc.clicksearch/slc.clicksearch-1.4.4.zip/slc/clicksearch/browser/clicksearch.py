import re 

from zope.component import getUtility
from zope.component import queryMultiAdapter

from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.clicksearch.interfaces import IClickSearchConfiguration
from slc.clicksearch.util import *


class ClickSearchView(BrowserView):
    """ The clicksearch view"""
    
    template = ViewPageTemplateFile('templates/clicksearch.pt')
    # template.id = '@@clicksearch'
    
    def __call__(self):
        self.query = query = current_query(self.request)        
        return self.template()

    def get_results(self, use_types_blacklist, use_navigation_root, sort_on, sort_order='reverse'):
        query = {'use_types_blacklist': use_types_blacklist,
                 'use_navigation_root': use_navigation_root,
                 'sort_on': sort_on,
                 'sort_order':sort_order,
                }
        external_q = self.context.buildQuery()
        if external_q:
            query.update(external_q)
        query.update(self.context.request.form)
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(query)

        # Place brains with sort_on attribute of '' at the back
        empty_valued_results = [r for r in results if hasattr(r, sort_on) and not getattr(r, sort_on)]
        results = results[len(empty_valued_results):] + results[0:len(empty_valued_results)]
        return results
    
    def generate_hidden_fields(self):
        out = []
        for q in self.query.keys():
            if q=='sort_on':
                continue
            out.append("""<input type="hidden" name="%s" value="%s">""" % (q, self.query[q]) )
        return "".join(out)
        
    def sort_criteria(self):
        settings = getUtility(IClickSearchConfiguration, name='clicksearch_config')
        cs = []
        for index in settings.sort_indexes:
            title = index.replace('_', ' ')
            pattern = re.compile('([A-Z][A-Z][a-z])|([a-z][A-Z])')
            title = pattern.sub(lambda m: m.group()[:1] + " " + m.group()[1:], title)
            title = title.replace('get ', '')
            if title[0].islower():
                title = title.capitalize()
            cs.append(dict(title=title, 
                           id=index, 
                           selected=self.request.get('sort_on','')==index))
        return cs
    
    def sort_order(self):
        sort_on = self.request.get('sort_on')
        if sort_on in ['sortable_title', 'Creator', 'subcategory']:
            return ''

        return 'reverse'

    def filed_under_link(self, subject):
        q = self.query.copy()
        q['Subject'] = subject
        new_qs = make_qs(q)
        return "clicksearch?%s" % new_qs  


    def displayResult(self, brain):
        view = queryMultiAdapter((self.context, self.request), 
                                      name='slc.clicksearch.result.%s' % brain.portal_type)
        if not view:
            view = queryMultiAdapter((self.context, self.request), 
                                        name='slc.clicksearch.result.generic')
        return view(brain)
