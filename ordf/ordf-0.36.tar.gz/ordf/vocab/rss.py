from ordf.graph import Graph
from logging import getLogger

log = getLogger(__name__)
rss_rdf = "http://purl.org/rss/1.0/schema.rdf"

def rdf_data():
    log.info("Fetching %s" % rss_rdf)
    g = Graph(identifier=rss_rdf).parse(rss_rdf)
    log.info("Parsed %s (%d triples)" % (rss_rdf, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.DLP.DLNormalization import NormalFormReduction
    rss = handler.get(rss_rdf)
    if len(rss) == 0:
        for rss in rdf_data():
            handler.put(rss)
    NormalFormReduction(rss)
    return network.setupDescriptionLogicProgramming(rss, addPDSemantics=False)
