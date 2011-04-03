from ordf.graph import Graph
from ordf.namespace import register_ns

register_ns("umbel", "http://umbel.org/umbel#")
register_ns("sc", "http://umbel.org/umbel/sc/")
register_ns("ac", "http://umbel.org/umbel/ac/")
register_ns("ne", "http://umbel.org/umbel/ne/")

from ordf.namespace import UMBEL, SC, AC, NE

from logging import getLogger
log = getLogger(__name__)

umbel_n3 = "http://umbel.org/ontology/umbel.n3"
ext_n3 = "http://umbel.org/ontology/umbel_external_ontologies_linkage.n3"

def rdf_data():
    def fetch(src):
        log.info("Fetching %s" % src)
        g = Graph(identifier=src).parse(src, format="n3")
        log.info("Parsed %s (%d triples)" % (src, len(g)))
        return g

    yield fetch(umbel_n3)
    yield fetch(ext_n3)
    yield fetch("http://umbel.org/ontology/umbel_subject_concepts.n3")
    yield fetch("http://umbel.org/ontology/umbel_abstract_concepts.n3")

def inference_rules(handler, network):
    from FuXi.DLP.DLNormalization import NormalFormReduction
    umbel = handler.get(umbel_n3)
    if len(umbel) == 0:
        umbel = Graph(identifier=umbel_n3).parse(umbel_n3, format="n3")
        handler.put(umbel)
    ext = handler.get(ext_n3)
    if len(ext) == 0:
        ext = Graph(identifier=ext_n3).parse(ext_n3, format="n3")
        handler.put(ext)
    onto = Graph()
    onto += umbel
    onto += ext
    NormalFormReduction(onto)
    return network.setupDescriptionLogicProgramming(onto, addPDSemantics=False)
