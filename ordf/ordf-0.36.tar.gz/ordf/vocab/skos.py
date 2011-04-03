from ordf.graph import Graph
from ordf.vocab.owl import predicate, object_predicate, \
    Class, Individual, AnnotatibleTerms
from logging import getLogger

log = getLogger(__name__)
skos_rdf = "http://www.w3.org/TR/skos-reference/skos.rdf"

from ordf.namespace import SKOS

class _Common(object):
    prefLabel = predicate(SKOS.prefLabel)
    altLabel = predicate(SKOS.altLabel)

class ConceptScheme(Class, _Common):
    topConcept = object_predicate(SKOS.topConcept, "Concept", globals())

    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa["skipClassMembership"] = True
        kwa.setdefault("factoryClass", Concept)
        super(ConceptScheme, self).__init__(*av, **kwa)
        if not kw.get("skipClassMembership"):
            self.type = SKOS.ConceptScheme

class Concept(Class, _Common):
    inScheme = object_predicate(SKOS.inScheme, ConceptScheme)
    topConceptOf = object_predicate(SKOS.topConceptOf, ConceptScheme)
    notation = predicate(SKOS.notation)
    narrower = object_predicate(SKOS.narrower, "Concept", globals())
    broader = object_predicate(SKOS.broader, "Concept", globals())

    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa["skipClassMembership"] = True
        kwa.setdefault("factoryClass", Concept)
        super(Concept, self).__init__(*av, **kwa)
        if not kw.get("skipClassMembership"):
            self.type = SKOS.Concept

class NotationCache(object):
    def __init__(self, store):
        self.cache = {}
        self.store = store
    def get(self, resource):
        from telescope import Select, v
        notation = self.cache.get(resource)
        if notation is None:
            q = Select([v.notation], distinct=True).where(
                (resource, SKOS.notation, v.notation)
                )
            for notation in self.store.query(q.compile()):
                if isinstance(notation, list): notation = notation[0]
                self.cache[resource] = notation
                break
        return notation

def rdf_data():
    log.info("Fetching %s" % skos_rdf)
    g = Graph(identifier=skos_rdf).parse(skos_rdf)
    log.info("Parsed %s (%d triples)" % (skos_rdf, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.DLP.DLNormalization import NormalFormReduction
    skos = handler.get(skos_rdf)
    if len(skos) == 0:
        for skos in rdf_data():
            handler.put(skos)
    NormalFormReduction(skos)
    return network.setupDescriptionLogicProgramming(skos, addPDSemantics=False)
