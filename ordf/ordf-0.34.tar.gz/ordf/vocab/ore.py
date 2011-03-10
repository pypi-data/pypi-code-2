__all__ = ["Aggregation"]

from ordf.graph import Graph
from ordf.namespace import RDF, ORE
from ordf.utils import get_identifier

class Aggregation(Graph):
    """
    This flavour of :class:`Graph` exposes aggregations
    as defined by the openarchives ORE vocabulary.
    """
    def __init__(self, *av, **kw):
        super(Aggregation, self).__init__(*av, **kw)
        if not self:
            self.add((self.identifier, RDF["type"], ORE["Aggregation"]))
        else:
            assert self.exists((self.identifier, RDF["type"], ORE["Aggregation"]))

    def aggregate(self, graph):
        self.add((self.identifier, ORE["aggregates"], graph.identifier))
        graph.add((graph.identifier, ORE["isAggregatedBy"], self.identifier))
        
    def contexts(self):
        for s,p,o in self.triples((self.identifier, ORE["aggregates"], None)):
            yield Graph(store=self.store, identifier=o)
