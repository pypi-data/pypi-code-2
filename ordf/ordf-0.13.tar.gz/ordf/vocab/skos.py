from ordf.graph import Graph
from ordf.vocab.owl import predicate, cached_predicate, Class, Individual, AnnotatibleTerms
from logging import getLogger

log = getLogger(__name__)
skos_rdf = "http://www.w3.org/TR/skos-reference/skos.rdf"

from ordf.namespace import SKOS

class _Common(object):
    prefLabel = cached_predicate(SKOS.prefLabel)
    altLabel = cached_predicate(SKOS.altLabel)
    notation = cached_predicate(SKOS.notation)
            
class ConceptScheme(Class, _Common):
    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa.setdefault("skipOWLClassMembership", True)
        super(ConceptScheme, self).__init__(*av, **kwa)
        self.type = SKOS.ConceptScheme
    def get(self, identifier=None, graph=None):
        if graph is None: graph=self.graph
        concept = ConceptInstance(identifier, graph=graph)
        concept.factoryGraph = graph
        return concept

    def addTop(self, concept):
        self.topConcept = concept

    def _get_topConcept(self):
        for concept in self.graph.distinct_objects(self.identifier, SKOS.topConcept):
            if self.graph.exists(concept, OWL.subClassOf, SKOS.Concept):
                yield Concept(concept, graph=self.graph)
            else:
                yield ConceptInstance(concept, graph=self.graph)
    def _set_topConcept(self, concept):
        self.graph.add((self.identifier, SKOS.topConcept, concept.identifier))
        concept.graph.add((concept.identifier, SKOS.topConceptOf, self.identifier))
        concept.inScheme = self
    topConcept = property(_get_topConcept, _set_topConcept)

class _ConceptCommon(_Common):
    def _get_inScheme(self):
        if not hasattr(self, "_inScheme_cache"):
            self._inScheme_cache = [Scheme(x, self.graph) for x in
                                    self.graph.distinct_objects(self.identifier, SKOS.inScheme)]
        return self._inScheme_cache
    def _set_inScheme(self, what):
        if isinstance(what, Individual): what = what.identifier
        self.graph.add((self.identifier, SKOS.inScheme, what))
        if hasattr(self, "_inScheme_cache"): del self._inScheme_cache
    inScheme = property(_get_inScheme, _set_inScheme)
    def _get_narrower(self):
        if not hasattr(self, "_narrower_cache"):
            self._narrower_cache = [ConceptInstance(x, self.graph) for x in 
                                    self.graph.distinct_objects(self.identifier, SKOS.narrower)]
        return self._narrower_cache
    def _set_narrower(self, what):
        if isinstance(what, Individual): what = what.identifier
        self.graph.add((self.identifier, SKOS.narrower, what))
        if hasattr(self, "_narrower_cache"): del self._narrower_cache
    narrower = property(_get_narrower, _set_narrower)
    def _get_broader(self):
        if not hasattr(self, "_broader_cache"):
            self._broader_cache = [ConceptInstance(x, self.graph) for x in 
                                    self.graph.distinct_objects(self.identifier, SKOS.broader)]
        return self._broader_cache
    def _set_broader(self, what):
        if isinstance(what, Individual): what = what.identifier
        self.graph.add((self.identifier, SKOS.broader, what))
        if hasattr(self, "_broader_cache"): del self._broader_cache
    broader = property(_get_broader, _set_broader)

class Concept(Class, _ConceptCommon):
    def __init__(self, *av, **kw):
        kwa = kw.copy()
        supers = set(kw.get("subClassOf", []))
        supers.add(SKOS.Concept)
        kwa["subClassOf"] = supers
        super(Concept, self).__init__(*av, **kwa)

class ConceptInstance(AnnotatibleTerms, _ConceptCommon):
    pass

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
