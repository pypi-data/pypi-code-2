from ordf.graph import Graph
from ordf.namespace import RDFS
import os, pkg_resources

from logging import getLogger
log = getLogger(__name__)

def rdf_data():
    graph_uri = RDFS[""]
    log.info("Fetching %s" % graph_uri)
    g = Graph(identifier=graph_uri).parse(graph_uri)
    log.info("Parsed %s (%d triples)" % (graph_uri, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.Horn.HornRules import HornFromN3
    rule_file = pkg_resources.resource_filename("ordf.vocab", os.path.join("n3", "rdfs-rules.n3"))
    rules = HornFromN3(rule_file)
    for rule in rules:
        network.buildNetworkFromClause(rule)

    from FuXi.DLP.DLNormalization import NormalFormReduction
    rdfs = handler.get(RDFS[""])
    if len(rdfs) == 0:
        for rdfs in rdf_data():
            pass
    NormalFormReduction(rdfs)
    dlp = network.setupDescriptionLogicProgramming(rdfs, addPDSemantics=True)

    return list(rules) + dlp
