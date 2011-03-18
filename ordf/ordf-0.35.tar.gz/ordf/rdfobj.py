__all__ = ["RDFObj"]

from ordf.term import URIRef
from ordf.namespace import RDF
from pprint import pformat

class RDFObj(object):
    def __init__(self, graph, subject):
        self.graph = graph
        self.subject = subject

    def __str__(self):
        types = [str(o) for s,p,o in self.graph.triples((self.subject, RDF.type, None))]
        dct = {
            "graph": self.graph.identifier,
            "subject": self.subject,
            "types": types
        }
        return pformat(dct)
    def __repr__(self):
        return str(self)

    def dict(self):
        dct = {}
        for s,p,o in self.graph.triples((self.subject, None, None)):
            dct.setdefault(p, []).append(o)
        return dct

    def keys(self):
        return self.dict().keys()
    def values(self):
        return self.dict().values()
    def items(self):
        return self.dict().items()

    def __getitem__(self, k):
        def iterpred():
            for s,p,o in self.graph.triples((self.subject, k, None)):
                if isinstance(o, URIRef):
                    yield RDFObj(self.graph, o)
                else:
                    yield o
        return list(iterpred())
