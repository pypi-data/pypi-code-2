import logging

from zope.component import getMultiAdapter
from zope.interface import Interface, implements, alsoProvides

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from slc.clicksearch.interfaces import ISelectView
from slc.clicksearch.util import *

log = logging.getLogger('slc.clicksearch.browser.widgets.py')

class BaseView(BrowserView):
    """ Basic functionality """
    implements (ISelectView)

    def __call__(self, index, box_config):
        self._index = index
        self.box_title = box_config[0]
        self.top = self._prepare_top(box_config[1])

        self.query = current_query(self.request)

        if index in self.request.keys():
            return self.template_selected()

        return self.template()

    def _prepare_top(self, top):
        new_top = []
        for t in top:
            t['id'] = t['title']
            t['title'] = self.prepare_title(t['id'])
            new_top.append(t)
        return new_top

    @property
    def index(self):
        return self._index


    def prepare_title(self, id):
        """ use some processing to find a human readable title for the given metadata element id
            like Musculoskeletal disorders for msd
            override in subclass
        """
        return _(id)

    def select_link(self, value):
        query = self.query
        query[self.index] = value
        new_qs = make_qs(query)
        return "clicksearch?%s" % new_qs

    def selected_value(self):
        return self.request.get(self.index)

    def caption(self):
        return self.prepare_title(self.selected_value())

    def unselect_link(self):
        """ returns the link which removes the current index from the query """
        query = self.query.copy()
        if query.has_key(self.index):
            del query[self.index]
        new_qs = make_qs(query)
        if new_qs:
            return "clicksearch?%s" % new_qs
        return "clicksearch"

    def see_more_link(self):
        """ returns the link to the view which allows selecting from the whole value set """
        query = current_query(self.request)
        query['selected_index'] = self.index
        query['index_title'] = self.box_title
        new_qs = make_qs(query)
        return "clicksearch-details?%s" % new_qs

    

class SimpleListView(BaseView):
    """ creates a view for a simple list metadatum """
    template = ViewPageTemplateFile('widgets/simple_list.pt')
    template_selected = ViewPageTemplateFile('widgets/simple_list_selected.pt')

    
class DropdownView(SimpleListView):
    """Creates a view for metadata requiring a dropdown box
    """
    template = ViewPageTemplateFile('widgets/dropdown.pt')
    template_selected = ViewPageTemplateFile('widgets/dropdown.pt')

    def link(self, index, elem):
        """ """
        return make_link(self.request, index, elem)

    def index_values(self):
        """Return the values from the index
        """
        cat = getToolByName(self.context, 'portal_catalog')
        idx = cat._catalog.getIndex(self.index)
        return idx.uniqueValues()


class ATVMTreeListView(SimpleListView):
    """Creates a view for a tree like metadatum based on atvm (use this for VDEX FILE Vocabs) 
    """
    template = ViewPageTemplateFile('widgets/tree_list.pt')
    template_selected = ViewPageTemplateFile('widgets/tree_list_selected.pt')

    # CAREFUL: THIS IS AN ABSTRACT CLASS. INHERIT AND SET vocabulary_name
    vocabulary_name = None

    def __call__(self, index, box_config):
        self._index = index
        self.box_title = box_config[0]
        self.top = self._prepare_top(box_config[1])

        self.query = current_query(self.request)

        vtool = getToolByName(self.context, 'portal_vocabularies')
        vocab = getattr(vtool, self.vocabulary_name)
        self.manager = vocab._getManager()

        self.reverse_dict = self.create_reverse_term_dict()

        if index in self.request.keys():
            return self.template_selected()

        return self.template()

    def selected_value_caption(self):
        return self.manager.getTermCaptionById(self.request.get(self.index))

    def getCaptionById(self, id):
        return self.manager.getTermCaptionById(id)

    def create_reverse_term_dict(self):
        """ create a dict which allows to resolve the parents"""
        vdict = self.manager.getVocabularyDict()
        reverse_dict = {}


        def register_parent(parent, dict):
            for k,v in dict.items():
                new_parent = k
                reverse_dict[k] = parent
                if v[1] is None:
                    continue
                register_parent(new_parent, v[1])

        register_parent(None, vdict)

        return reverse_dict

    def get_current_tree(self):
        term = self.selected_value()
        term_node = self.manager.getTermById(term)
        termsdict = self.manager.getTerms(term_node)

        if termsdict is not None:
            terms = termsdict.copy()
            for T in termsdict.keys():
                terms[T] = (termsdict[T][0], None)
        else:
            terms = None

        #query = current_query(self.request)
        # go through the tree from toe til top, resolving the parents of term
        while True:
            if term is None:
                break
            caption = self.manager.getTermCaptionById(term)
            terms = {term : (caption, terms)}
            term = self.reverse_dict.get(term)


        return terms


class ATVMVDEXTreeListView(SimpleListView):
    """ creates a view for a vdex tree like metadatum based on atvm (use this for VDEX VOcabs) """
    template = ViewPageTemplateFile('widgets/tree_list.pt')
    template_selected = ViewPageTemplateFile('widgets/tree_list_selected.pt')

    # CAREFUL: THIS IS AN ABSTRACT CLASS. INHERIT AND SET vocabulary_name
    vocabulary_name = None

    def __call__(self, index, box_config):
        self._index = index
        self.box_title = box_config[0]
        self.top = self._prepare_top(box_config[1])

        self.query = current_query(self.request)

        vtool = getToolByName(self.context, 'portal_vocabularies')
        self.vocab = getattr(vtool, self.vocabulary_name)

        if index in self.request.keys():
            return self.template_selected()

        return self.template()

    def selected_value_caption(self):
        id = self.request.get(self.index)
        return self.getCaptionById(id)

    def getCaptionById(self, id):
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(path='/'.join(self.vocab.getPhysicalPath()), id=id, portal_type='VdexTerm')
        if len(res)==0:
            return id
        return res[0].Title

    def _getTermById(self, id):
        pc = getToolByName(self.context, 'portal_catalog')
        res = pc(path='/'.join(self.vocab.getPhysicalPath()), id=id, portal_type='VdexTerm')
        if len(res) == 0:
            return None
        return res[0]

    def get_current_tree(self):
        pc = getToolByName(self.context, 'portal_catalog')
        term = self.selected_value()
        term_node = self._getTermById(term)
        term_node_ob = term_node.getObject()

        # All items below the current term
        res = pc(path=term_node.getPath(), portal_type='VdexTerm')
        terms = {}
        for r in res:
            if r.getPath()==term_node.getPath():
                continue
            terms[r.id] = (r.Title, None)

        while term_node_ob.portal_type == 'VdexTerm':
            term = term_node_ob.id
            caption = term_node_ob.Title()
            terms = {term: (caption, terms)}
            term_node_ob = term_node_ob.aq_parent

        return terms


class PortalTypeView(SimpleListView):
    """ creates a view for the portal_type metadatum """

    def prepare_title(self, id):
        ttool = getToolByName(self.context, 'portal_types')
        info = ttool.getTypeInfo(id)
        if not info:
            log.error('%s not registered in portal_types' %id)
            return 
        type_name = _(info.Title())
        return type_name


