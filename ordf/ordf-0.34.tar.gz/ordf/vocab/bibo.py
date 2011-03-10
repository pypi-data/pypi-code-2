from ordf.graph import Graph
from ordf.namespace import BIBO
from logging import getLogger

log = getLogger(__name__)

def rdf_data():
    log.info("Fetching %s" % BIBO)
    g = Graph(identifier=BIBO[""]).parse(BIBO)
    log.info("Parsed %s (%d triples)" % (BIBO, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.DLP.DLNormalization import NormalFormReduction
    bibo = handler.get(BIBO[""])
    if len(bibo) == 0:
        for bibo in rdf_data():
            handler.put(bibo)
    NormalFormReduction(bibo)
    return network.setupDescriptionLogicProgramming(bibo, addPDSemantics=False)
