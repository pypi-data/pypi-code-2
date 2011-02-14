from ordf.vocab.owl import predicate, AnnotatibleTerms, Class
from ordf.namespace import DC, FOAF, OWL, RDF, RDFS, VOID

class Dataset(Class):
    def __init__(self, *av, **kw):
        super(Dataset, self).__init__(VOID.Dataset, *av, **kw)
    def get(self, identifier, graph=None):
        if graph is None: graph=self.graph
        ds = _Dataset(identifier, graph=graph)
        ds.factoryGraph = ds.graph
        ds.type = self.identifier
        return ds
    
class _Dataset(AnnotatibleTerms):
    # xxx should we put DC and FOAF things like this somewhere
    # in a superclass? hard to do without inappropriately
    # hardwiring a class hierarchy
    title = predicate(DC["title"])
    description = predicate(DC.description)
    isPartOf = predicate(DC.isPartOf)
    homepage = predicate(FOAF.homepage)
    page = predicate(FOAF.page)

    subset = predicate(VOID.subset)
    dataDump = predicate(VOID.dataDump)
    vocabulary = predicate(VOID.vocabulary)
    sparqlEndpoint = predicate(VOID.sparqlEndpoint)
    exampleResource = predicate(VOID.exampleResource)
