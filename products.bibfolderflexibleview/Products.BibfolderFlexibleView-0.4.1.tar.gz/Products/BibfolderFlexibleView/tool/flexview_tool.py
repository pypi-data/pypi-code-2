

# TODO was muss private etc.? 


from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.Folder import Folder
from Products.BibfolderFlexibleView.config import MASKS
from Products.BibfolderFlexibleView.config import CATEGORIES
from AccessControl import Unauthorized
from types import UnicodeType
from types import ListType
from types import TupleType
from types import StringType
from types import DictType
from safe_eval import *

class FlexviewTool(UniqueObject, Folder):
    id = 'portal_bibliography_flexible_view'
    meta_type = 'Bibliography Flexible View Tool'
    
    __allow_access_to_unprotected_subobjects__ = 1
    
    # XXX bessere defaults finden!
    #pubentry_mask = 'deprecated'
    #pubentry_mask_unparsed = 'deprecated'
    #pubentry_fields = ['deprecared']
    pubentry_lead_in = '<dl>'
    pubentry_lead_out = '</dl>'
    pubentry_use_ao = True
    pubentry_ao_path = ''
    pubentry_ao_lead_in = '<ul>'
    pubentry_ao_lead_out = '</ul>'
    pubentry_ao_mask = "<li><a href='%s'>%s</a></li>"
    pubentry_ao_mask_unparsed = "<li><a href='%u'>%T</a></li>"
    pubentry_ao_fields = ['url', 'title']
    publication_url_as_ao = True
    publication_url_ao_title = 'Information/Download'
    publication_url_ao_ico = 'link_icon.gif'
    pdf_file_as_ao = False
    pdf_file_ao_title = 'Download as pdf-file'
    pdf_file_ao_ico = ''
    authors_from_references = True
    authors = []
    ao_show_priv = False
    use_ao_ip_check = False
    ao_ip_check_keyword = ''
    ao_ip_check_range = ''
    num_unparsed_masks = 0
    highest_category_idx = 0
    
    _properties = Folder._properties + (
            #{'id':'pubentry_mask',
            # 'type':'string',
            # 'mode':'w'   
            #},
            #{'id':'pubentry_mask_unparsed',
            # 'type':'string',
            # 'mode':'w'   
            #},
            #{'id':'pubentry_fields',
            # 'type':'lines',
            # 'mode':'w'   
            #},
            {'id':'pubentry_lead_in',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_lead_out',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_ao_path',
             'type':'string',
             'mode':'w'
            },
            {'id':'pubentry_ao_lead_in',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_ao_lead_out',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_ao_mask',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_ao_fields',
             'type':'lines',
             'mode':'w'   
            },
            {'id':'pubentry_use_ao',
             'type':'boolean',
             'mode':'w'   
            },
            {'id':'authors_from_references',
             'type':'boolean',
             'mode':'w'   
            },
            {'id':'authors',
             'type':'lines',
             'mode':'w'   
            },
            {'id':'publication_url_as_ao',
             'type':'boolean',
             'mode':'w'   
            },
            {'id':'publication_url_ao_title',
             'type':'string',
             'mode':'w'   
            },
            {'id':'publication_url_ao_ico',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pdf_file_as_ao',
             'type':'boolean',
             'mode':'w'   
            },
            {'id':'pdf_file_ao_title',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pdf_file_ao_ico',
             'type':'string',
             'mode':'w'   
            },
            {'id':'pubentry_ao_mask_unparsed',
             'type':'string',
             'mode':'w'   
            },
            {'id': 'ao_show_priv',
             'type':'boolean',
             'mode':'w'   
            },
            {'id': 'use_ao_ip_check',
             'type':'boolean',
             'mode':'w'   
            },
            {'id':'ao_ip_check_keyword',
             'type':'string',
             'mode':'w'   
            },
            {'id':'ao_ip_check_range',
             'type':'string',
             'mode':'w'   
            },
            {'id':'num_unparsed_masks',
             'type':'int',
             'mode':'w' 
            },
            {'id':'highest_category_idx',
             'type':'int',
             'mode':'w' 
            })
    
    # manche keys sind doppelt belegt, welcher benutzt wird, haengt von 'allowed_fields' ab
    # fehlt: citationLabel
    keymap = {#'A': ['authors'],
          'A': ['Authors'],
          #'T': ['title'],
          'T': ['Title', 'title'],
          'm': ['publication_month'],
          'y': ['publication_year'],
          'J': ['journal'],
          'I': ['institution', 'id'],
          'O': ['organization'],
          'B': ['booktitle'],
          'r': ['preprint_server'],
          'v': ['volume'],
          'n': ['number'],
          'E': ['editor'],
          'p': ['pages'],
          'a': ['address'],
          'i': ['pmid', 'ico'],
          'e': ['edition'],
          'h': ['howpublished'],
          'c': ['chapter'],
          's': ['series'],
          't': ['publication_type'],
          #'t': ['type'],
          # ATBiblioList bekannt aber nicht in der legende:
          'S': ['school'],
          # neu hier (u.a. fuer associated objects):
          'o': ['ass_obs'],
          'l': ['absolute_url'],
          # getRemoteUrl gibts offenbar nur bei brains?
          #'l': ['absolute_url', 'getRemoteUrl'],
          'u': ['publication_url', 'url'],
          'src': ['Source'],
          #'abs': ['abstract']
          'abs': ['abstract', 'Description'],
          'doi': ['DOI'],
          'P': ['publisher'],
          'isbn': ['isbn'],
          'priv': ['priv'],
          'desc': ['Description']
          }
    # XXX vllt doch eher Description statt abstract, weil das auch im Katalog ist! Oder beide
    pubentry_allowed = [#'authors',
                    'Authors',
                    #'title', 
                    'Title',
                    'publication_month', 
                    'publication_year', 
                    'journal', 
                    'institution', 
                    'organization',
                    'booktitle',
                    'preprint_server',
                    'volume',
                    'number',
                    'editor',
                    'pages',
                    'address',
                    'pmid',
                    'edition',
                    'howpublished',
                    'chapter',
                    'series',
                    'publication_type',
                    #'type',
                    'school',
                    'absolute_url',
                    #'getRemoteUrl',
                    'publication_url',
                    'ass_obs',
                    'Source',
                    'abstract',
                    # offenbar enthaelt description das plain-text abstract
                    #'Description',
                    'DOI',
                    'publisher',
                    'isbn']
    
    
    pubentry_ao_allowed = ['id', 'title', 'ico', 'url', 'priv', 'desc']
    
    label_alias = {'Source': '',
                   'ass_obs': '',
                   'absolute_url': '',
                   'id': '',
                   'ico': '',
                   'url': '',
                   'priv': '',
                   'desc': '',
                   #'type': 'publication_type',
                   'publication_url': 'url'}   
    
    #    def __init__(self):
    
    def __post_init__(self):    
        bibtool = getToolByName(self, 'portal_bibliography')
        reftypes = bibtool.getReferenceTypes()
        self.add_ref_type_mask_properties(self, reftypes)
        for m in MASKS:
            self.add_mask(self, mask=m, reftypes=MASKS[m])
        self.process_masks(self)
        for c in CATEGORIES:
            self.add_category(self, category=c, reftypes=CATEGORIES[c])
            
            # wenn es alle felder die wir brauchen auch als catalog-metadata gibt, sparen wir viel zeit
            # gebe alle felder aus pubentry_allowed zurueck, die auch in brains vorkommen - plus ass_obs
    def get_catalog_compatible_fields(self):
        catalog = getToolByName(self, 'portal_catalog')
        return [x for x in self.pubentry_allowed if x in catalog.schema()] + ['ass_obs']
        
        
    def process_masks(self, prop_src, REQUEST=None):
        bibtool = getToolByName(self, 'portal_bibliography')
        reftypes = bibtool.getReferenceTypes()
        self.add_ref_type_mask_properties(prop_src, reftypes)
        
        #aopm = self.parse_mask(REQUEST['pubentry_ao_mask_unparsed'], self.pubentry_ao_allowed)
        aopm = self.parse_mask(prop_src['pubentry_ao_mask_unparsed'], self.pubentry_ao_allowed)
        prop_src.manage_changeProperties({'pubentry_ao_mask': aopm['mask']})
        prop_src.manage_changeProperties({'pubentry_ao_fields': aopm['fields']})
        
        # welche unparsed_masks gibt es ueberhaupt
        indices = []
        for i in range(prop_src.num_unparsed_masks):
            #if REQUEST and REQUEST.has_key('unparsed_mask_%i' % i): indices += [i]
            if prop_src.hasProperty('unparsed_mask_%i' % i): indices += [i]
            
            #inmasks = [{'mask': REQUEST['unparsed_mask_%i' % i], 'reftypes': REQUEST['unparsed_mask_%i_reftypes' % i]}
        inmasks = [{'mask': prop_src['unparsed_mask_%i' % i], 'reftypes': prop_src['unparsed_mask_%i_reftypes' % i]}
                        for i in indices]
        
        # wir drehen die reihenfolge um, damit die *ersten* eintraege, die einen reftype enthalten, sich durchsetzen
        inmasks.reverse() 
        for m in inmasks:
            for rtype in m['reftypes']:
                pm = self.parse_mask(m['mask'], self.pubentry_allowed)
                prop_src.manage_changeProperties({rtype + '_mask': pm['mask']})
                prop_src.manage_changeProperties({rtype + '_fields': pm['fields']})
                
    def add_ref_type_mask_properties(self, prop_src, reftypes):
        # wird auch nach jedem config aufgerufen, damit wir evtl neuregistrierte reference-types mitnehmen
        pmap =  prop_src.propertyMap()
        for rtype in reftypes:
            if not rtype + '_mask' in [p['id'] for p in pmap]:
                prop_src.manage_addProperty(type="string", id=rtype+'_mask', value='')
                prop_src.manage_addProperty(type="lines", id=rtype+'_fields', value='')
                
    def parse_mask(self, inmask, allowed_fields): 
        outfields = []
        
        i = 0
        replaceme = ['%' + x for x in self.keymap.keys()]
        while i < len(inmask):
            if inmask[i] == '%' or inmask[i] == '$':
                found_key = False
                for k in self.keymap.keys():
                    if inmask.find(k, i + 1, i + 1 + len(k)) > -1:
                        found_key = True
                        if set(self.keymap[k]).intersection(set(allowed_fields)) == set([]):
                            raise ValueError, "'%%%s'/'$%s' not allowed here" % (k, k)
                        for f in self.keymap[k]:
                            if f in allowed_fields:
                                field = f
                                break
                        if inmask[i] == '%':
                            outfields.append(field)
                            i += len(k)
                        else: # inmask[i] == '$', wir haben etwas mehr zu tun
                            if inmask[i + len(k) + 1] != '{':
                                raise ValueError, "'{' expected after condition '$%s'" % k
                            j = inmask.find('}', i + len(k) + 2)
                            if j < 0:
                                raise ValueError, "closing '}' expected"
                            cs = inmask[i + len(k) + 2 : j]
                            if '%' in cs:
                                raise ValueError, "no placeholders allowed in conditional statements"
                            if '$' in cs:
                                raise ValueError, "no nested conditional statements allowed"
                            outfields.append('$' + field + '$' + cs)
                            replaceme.insert(0, inmask[i : j + 1])
                            
                            i = j
                        break
                if not found_key and inmask[i + 1] not in '%$' < 0:
                    raise ValueError, "invalid key at pos %i ('%s')" % (i, inmask[i:min(i+2,len(inmask))])                        
            else:
                i += 1
        outmask = inmask    
        for k in replaceme:
            outmask = outmask.replace(k, '%s')
            
        return {'mask': outmask, 'fields': outfields}
        
    def get_unparsed_masks(self, prop_src):
        l = []
        for i in range(prop_src.num_unparsed_masks):
            k = "unparsed_mask_%i" % i
            if prop_src.hasProperty(k):
                l += [{'id': k, 'mask': prop_src[k], 'reftypes': prop_src[k + '_reftypes']}]
        return l
        
        
        
    def get_categories(self, prop_src):
        l = []
        for i in range(prop_src.highest_category_idx):
            k = "category_%i" % i
            if prop_src.hasProperty(k):
                l += [{'id': k, 'category': prop_src[k], 'reftypes': prop_src[k + '_reftypes']}]
        return l
        
    def query_from_string(self, s):
        if isinstance(s, StringType):
            return safe_eval(s)
        else: return s
        
        # merge our query 'query' with topic query 'q'
    def merge_queries(self, query, q):
        for k, v in q.items():
            if query.has_key(k):
                arg = query.get(k)
                #print k, v, arg
                ## sonderbehandlung path
                #if k == 'path' and isinstance(arg, StringType) and isinstance(v, DictType):
                #    query[k] = v
                #    if arg in v['query']:
                #        query[k]['query'] = [arg]
                #    else:
                #        query[k]['query'] = []
                # ab hier wie in attopic                            
                if isinstance(arg, (ListType,TupleType)) and isinstance(v, (ListType,TupleType)):
                    query[k] = [x for x in arg if x in v]
                elif isinstance(arg, StringType) and isinstance(v, (ListType,TupleType)) and arg in v:
                    query[k] = [arg]
                elif isinstance(arg, StringType) and isinstance(v, StringType):
                    # here we differ from the ATTopic code this was copied from...
                    # this kind of behaviour is what we want for SearchableText, it may
                    # not make sense for other string criteria which aren't (yet?) used in
                    # BibfolderFlexibleView
                    query[k]= v + ' ' + arg
                else:
                    query[k]= v
            else:
                query[k] = v
        return query
        
    def is_get_object_authorized(self, brain):
        try:
            brain.getObject()
        except Unauthorized:
            return False
        return True
        
    def get_legend(self, allowed_fields):
        l = []
        cafs = self.get_catalog_compatible_fields()
        for k in self.keymap.keys():
            if set(self.keymap[k]).intersection(set(allowed_fields)) != set([]):
                for f in self.keymap[k]: 
                    if f in allowed_fields:
                        d = {'placeholder': '%' + k, 'field': f, 'in_catalog': f in cafs}
                        if self.label_alias.has_key(f):
                        # die folgende and or orgie ist eigentlich absurd
                            d['label'] = ((self.label_alias[f] and 'label_') or f) + self.label_alias[f]
                            d['help'] = ((self.label_alias[f] and 'help_') or f) + self.label_alias[f]
                        else:
                            d['label'] = 'label_' + f.lower()
                            d['help'] = 'help_' + f.lower()
                            
                        l.append(d)
                        break     
        return l    
        
        # erwartet in inlist die brains aus dem catalog, *nicht* die objekte selbst  
    def get_formatted_list(self, prop_src, inlist, ass_obs = []):
    
        def _uc(s):
            if type(s) is not UnicodeType:
                s = unicode(s, 'utf-8', 'replace')    
            return s
            
        def _get(obj, attr):
            if isinstance(obj, DictType):
                a = obj[attr]
            else:
                a = getattr(obj, attr)
                if hasattr(a, '__call__'): 
                    a = a()
            return _uc(a)
            
        def _fill_mask(mask, obj, fields, ao_str = ''):
            v = ()
            for f in fields:
                if f.startswith('$'):
                    cf, va = f.lstrip('$').split('$')
                    v += (_get(obj, cf) and _uc(va),)
                else:
                    if f == 'ass_obs':
                        v += (ao_str,)
                    else: 
                        v += (_get(obj,f),)
            return mask % v
            
        outlist = []
        
        bibtool = getToolByName(self, 'portal_bibliography')
        reftypes = bibtool.getReferenceTypes()
        # if not all fields are catalog compatible or pdf_file_as_ao is set, 
        # fall back to the real objects
        for rt in reftypes:
            if not set(prop_src[rt + '_fields']).issubset(set(self.get_catalog_compatible_fields())) or prop_src.pdf_file_as_ao:
                # catch Unauthorized exception in order to ignore 'private' references
                il = []
                for x in inlist:
                    try:
                        if x.getObject(): il += [x.getObject()]
                    except Unauthorized:
                        pass
                inlist = il
                break
                
        for r in inlist:        
            #v = ()  
            s = u''
            
            # first, turn all aos into a string using lead-in/out + mask
            # this looks messier than it is due to the various special cases
            if prop_src.pubentry_use_ao:
                # pdfs as aos?
                if prop_src.pdf_file_as_ao and (r.getPdf_file() or r.getPdf_url()):
                    if r.getPdf_file():
                        pdf = r.getPdf_file()
                        pdf_ao = {'id': pdf.id, 
                                  'title': prop_src.pdf_file_ao_title, 
                                  'url': pdf.absolute_url(), 
                                  'ico': prop_src.pdf_file_ao_ico or pdf.getIcon(),
                                  'priv': ''}
                    elif r.getPdf_url():
                        pdf = r.getPdf_url()
                        pdf_ao = {'id': r.id, 
                                  'title': prop_src.pdf_file_ao_title, 
                                  'url': pdf, 
                                  'ico': prop_src.pdf_file_ao_ico,
                                  'priv': ''}
                    if not ass_obs.has_key(r.id): ass_obs[r.id] = [pdf_ao]
                    else: ass_obs[r.id].insert(0, pdf_ao)
                    # url as ao?
                if prop_src.publication_url_as_ao and (r.publication_url != ''):
                    url_ao = {'id': r.id, 
                              'title': prop_src.publication_url_ao_title, 
                              'url': r.publication_url, 
                              'ico': prop_src.publication_url_ao_ico,
                              'priv': ''}
                    if not ass_obs.has_key(r.id): ass_obs[r.id] = [url_ao]
                    else: ass_obs[r.id].insert(0, url_ao)
                    
                if ass_obs.has_key(r.id):
                    s = _uc(prop_src['pubentry_ao_lead_in'])
                    
                    for ao in ass_obs[r.id]:
                        #v_ao = ()
                        ## XXX das steht unten nochma so aehnlich -> irgendwie buendeln
                        #for f in prop_src.pubentry_ao_fields: 
                        #    if f.startswith('$'):
                        #        cf, va = f.lstrip('$').split('$')
                        #        v_ao += (_uc(ao[cf]) and _uc(va),) 
                        #    else:
                        #        v_ao += (_uc(ao[f]),)
                        #s += _uc(prop_src['pubentry_ao_mask']) % v_ao
                        s += _fill_mask(_uc(prop_src['pubentry_ao_mask']), 
                                            ao,
                                            prop_src.pubentry_ao_fields)
                    s += _uc(prop_src['pubentry_ao_lead_out'])    
                    
                    #for f in prop_src[r.meta_type + '_fields']:
                    #    if f.startswith('$'):
                    #        cf, va = f.lstrip('$').split('$')
                    #        v += (_get(r, cf) and _uc(va),)
                    #    else:
                    #        if f == 'ass_obs':
                    #            v += (s,)
                    #        else: 
                    #            v += (_get(r,f),)
                    
                    #outlist += [_uc(prop_src[r.meta_type + '_mask']) % v]
            outlist += [_fill_mask(_uc(prop_src[r.meta_type + '_mask']),
                                   r,
                                   prop_src[r.meta_type + '_fields'],
                                   s)] 
        return outlist
        
        # XXX not a good way of returning this and should become obsolete... now?        
    def get_types(self, prop_src):        
        pub_types = {}
        for c in self.get_categories(prop_src):
            pub_types[c['category']] = c['reftypes']   
        return pub_types;
        
    def group_by_years(self, reflist):
        # nimmt eine liste von References (oder Brains!), gibt ein dictionary zurueck, in dem der key das jahr ist 
        # und zu jedem key die liste der references in diesem jahr gehoert
        res = {}
        for r in reflist:        
            year = r.publication_year
            if not res.has_key(year):
                res[year] = [r]
            else: res[year].append(r)
        return res
        
    def copy_tool_properties(self, prop_src, force_it=False):
        if force_it or not prop_src.hasProperty('pubentry_ao_mask'):
            for p in self.propertyMap():
                if not prop_src.hasProperty(p['id']) and p['id'] != 'title':
                    prop_src.manage_addProperty(type=p['type'], id=p['id'], value=self[p['id']])
                    prop_src.manage_changeProperties({p['id']: self[p['id']]})    
                    
    def count_seq_prop(self, prop_src, id):
        n = 0
        for i in range(prop_src.num_unparsed_masks):
            if prop_src.hasProperty(id % i): n += 1
        return n    
        
        # TODO fuer "num_unparsed_masks" waere highest_mask_idx oder so passender    
    def add_mask(self, prop_src, mask='', reftypes=[]):
        n = prop_src.num_unparsed_masks
        prop_src.manage_addProperty(type='string', id="unparsed_mask_%i" % n, value=mask)
        prop_src.manage_addProperty(type='lines', id="unparsed_mask_%i_reftypes" % n, value=reftypes)
        prop_src.manage_changeProperties({'num_unparsed_masks': n + 1})
        
    def delete_mask(self, prop_src, ids):
        n = self.count_seq_prop(prop_src, 'unparsed_mask_%i')
        if (n - len(ids)) < 1:
            raise ValueError, "you've got to keep at least one mask"
        prop_src.manage_delProperties(ids + [x + '_reftypes' for x in ids])
        
    def add_category(self, prop_src, category='', reftypes=[]):
        n = prop_src.highest_category_idx
        prop_src.manage_addProperty(type='string', id="category_%i" % n, value=category)
        prop_src.manage_addProperty(type='lines', id="category_%i_reftypes" % n, value=reftypes)
        prop_src.manage_changeProperties({'highest_category_idx': n + 1})
        
    def delete_category(self, prop_src, ids):
        n = self.count_seq_prop(prop_src, 'category_%i')
        if (n - len(ids)) < 1:
            raise ValueError, "you've got to keep at least one category"
        prop_src.manage_delProperties(ids + [x + '_reftypes' for x in ids]) 
