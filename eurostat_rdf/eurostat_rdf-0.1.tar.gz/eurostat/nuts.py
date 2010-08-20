"""
.. autoclass:: Regions
    :show-inheritance:
.. autoclass:: Region
    :show-inheritance:
"""
from ordf.graph import ConjunctiveGraph, Graph
from ordf.term import BNode, Literal, URIRef 
from ordf.vocab.skos import ConceptScheme, Concept, ConceptInstance
from ordf.namespace import register_ns, Namespace
register_ns("nutss", Namespace("http://purl.org/okfn/def/eurostat/nuts#"))
register_ns("nuts", Namespace("http://purl.org/okfn/id/eurostat/nuts#"))
register_ns("eurostat", Namespace("http://www4.wiwiss.fu-berlin.de/eurostat/resource/eurostat/"))
register_ns("regions", Namespace("http://www4.wiwiss.fu-berlin.de/eurostat/resource/regions/"))

from ordf.namespace import NUTS, NUTSS, REGIONS, EUROSTAT, RDF, RDFS, SKOS, OWL
from telescope import Select, v
from urllib import unquote

log = __import__("logging").getLogger(__name__)

class Regions(ConceptScheme):
    """
    NUTS regions as an (incomplete) SKOS concept Scheme.

    >>> regions = Regions()
    >>> regions.load()
    >>> scotland = regions.byName("scotland")
    >>> print [str(name) for name in scotland.label]
    ['Scotland']
    >>>

    .. automethod:: load
    .. automethod:: byName
    """
    def __init__(self, graph=None):
        if graph is None: graph = Graph()
        super(Regions, self).__init__(NUTSS.Regions, graph=graph)
        self.comment = Literal("The collection of regions that exist in the CRA as a concept scheme", lang="en")
        self.graph.add((self.identifier, RDFS.isDefinedBy, self.graph.identifier))
        self.graph.add((self.identifier, SKOS.prefLabel, Literal("regions", lang="en")))
        self._regionCache = {}

    def load(self, graph=None):
        """
        Load NUTS regions into the given *graph* (or *self.graph* if *None*)
        from the Frei Universitat Berlin.
        """
        if graph is None: graph = self.graph
        from rdflib.store.SPARQL import SPARQLStore
        log.info("Loading NUTS Regions from the Frei Universitat")
        fubs = SPARQLStore("http://www4.wiwiss.fu-berlin.de/eurostat/sparql")
        fub = ConjunctiveGraph(fubs)
        q = Select([v.subj, v.pred, v.obj], distinct=True).where(
            (v.subj, RDF.type, EUROSTAT.regions),
            (v.subj, v.pred, v.obj)
            )
        regions = Graph()
        [regions.add(s) for s in fub.query(q.compile())]
        for fuid in regions.distinct_subjects():
            log.info("Loading %s" % fuid)
            _s, _p, notation = regions.one((fuid, EUROSTAT.name_encoded, None))
            notation = Literal(notation.lower().replace("-", "_"))
            ident = NUTS[notation]
            region = self.get(ident, graph)
            region.type = NUTSS.Region
            region.isDefinedBy = NUTS[""]
            region.inScheme = self
            region.notation = Literal(unquote(notation))
            _s, _p, label = regions.one((fuid, EUROSTAT.name, None))
            region.label = label
            region.prefLabel = label
            region.graph.add((ident, OWL.equivalentClass, fuid))
            for _s, _p, parent in regions.triples((fuid, EUROSTAT.parentcountry, None)):
                pfx = "http://www4.wiwiss.fu-berlin.de/eurostat/resource/countries/"
                parent_notation = parent[len(pfx):].lower().replace("-", "_")
                parent = self.get(NUTS[parent_notation], graph)
                parent.type = NUTSS.Region
                parent.inScheme = self
                parent.notation = Literal(unquote(parent_notation))
                region.broader = parent
                parent.narrower = region
                self.addTop(parent)

        outside = self.get(NUTS.outside_uk, graph)
        outside.type = NUTSS.Region
        outside.isDefinedBy = NUTS[""]
        outside.label = Literal("Outside UK", lang="en")
        outside.prefLabel = Literal("Outside UK", lang="en")
        outside.notation = Literal("outside_uk")
        self.addTop(outside)

        nonident = self.get(NUTS.non_identifiable, graph)
        nonident.type = NUTSS.Region
        nonident.isDefinedBy, NUTS[""]
        nonident.label, Literal("Non-Identifiable", lang="en")
        nonident.prefLabel, Literal("Non-Identifiable", lang="en")
        nonident.notation, Literal("non_identifiable")
        self.addTop(nonident)

    def byName(self, name, graph=None):
        """
        Return an instance for the given *name*, optionally  from
        the given *graph* (otherwise from the store backing *self.graph*)
        and cache the result.
        """
        if graph is None: 
            graph=ConjunctiveGraph(self.graph.store)
        name = name.lower()
        if name.startswith("england_"):
            name = name[8:]
        if name == "east":
            name = "east of england"
        region = self._regionCache.get(name)

        if region is None:
            q = Select([v.ident, v.label], distinct=True).where(
                (v.ident, SKOS.inScheme, self.identifier),
                (v.ident, SKOS.prefLabel, v.label)
                )
            for ident, label in self.graph.query(q.compile()):
                if label.lower() == name:
                    region = self.get(ident, graph=graph)
                    break
            self._regionCache[name] = region
        if region is None:
            raise KeyError(name)
        return region

class Region(Concept):
    """
    The concept of a NUTS region.
    """
    def __init__(self, scheme):
        super(Region, self).__init__(NUTSS.Region, graph=scheme.graph)
        self.scheme = scheme
        self.graph.add((self.identifier, RDFS.isDefinedBy, self.graph.identifier))
        self.graph.add((self.identifier, SKOS.prefLabel, Literal("CRA/NUTS Region", lang="en")))

def rdf_data():
    schema = Graph(identifier=NUTSS[""])
    regions = Regions(schema)
    Region(regions)

    individuals=Graph(identifier=NUTS[""])
    regions.load(individuals)
    yield schema
    yield individuals

if __name__ == '__main__':
    import doctest
    import logging
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()
