from .base import *

register_ns("BIBLIOENTRY", Namespace("http://bibliographica.org/entry/"))
from ordf.namespace import BIBLIOENTRY, FOAF, SKOS, BIO, OWL, RDFS

class Concept(DomainObject):
    '''An subject/concept, typically that of a skos:concept
    '''
    namespace = BIBLIOENTRY
    
    label = predicate(RDFS.label)
    inscheme = predicate(SKOS.inScheme)
    notation = predicate(SKOS.notation)
    preflabel = predicate(SKOS.prefLabel)

    def __init__(self, *av, **kw):
        super(Concept, self).__init__(*av, **kw)
        self.type = SKOS.Concept

    @classmethod
    def find(self, limit=20, offset=0):
        ### should really use a lens (upgrade the bibo lens to
        ### understand about accounts and just display the
        ### account graph in here. no need for this find
        ### method...
        sparql_select = '''
        SELECT DISTINCT ?id
        WHERE {
            ?bnode a %(class_)s .
            ?bnode <http://www.w3.org/2002/07/owl#sameAs> ?id .
        } OFFSET %(offset)s LIMIT %(limit)s
        '''
        params = dict(
            class_='<%s>' % FOAF.Agent,
            limit=limit,
            offset=offset)
        query = sparql_select % params
        def cvt(qresult):
            return URIRef(qresult[0])
        results = map(cvt, handler.query(query))
        results = [self.get_by_uri(uri) for uri in results]
        return results

