from ordf.graph import ConjunctiveGraph, Graph
from ordf.vocab.owl import predicate, Ontology, Class, Property, AnnotatibleTerms
from ordf.term import URIRef, Literal
from ordf.namespace import SDMX, SDMXDIM, SDMXATTR, VOID, OWL, DC

class DataSet(Class):
    def __init__(self, graph=None):
        super(DataSet, self).__init__(
            SDMX.DataSet,
            subClassOf = [VOID.DataSet],
            graph=graph)
    def get(self, identifier, graph=None):
        if graph is None: graph = self.graph
        ds = _DataSet(identifier, graph=graph)
        ds.type = self.identifier
        ds.factoryGraph = ds.graph
        return ds

class _DataSet(AnnotatibleTerms):
    source = predicate(DC.source)
    isPartOf = predicate(DC.isPartOf)
    structure = predicate(SDMX.structure)
    series = predicate(SDMX.slice)
    
class DataStructureDefinition(Class):
    def __init__(self, graph=None):
        super(DataStructureDefinition, self).__init__(
            SDMX.DataStructureDefinition,
            graph=graph)
    def get(self, identifier=None, graph=None):
        if graph is None: graph = self.graph
        dsd = _DataStructureDefinition(identifier=identifier, graph=graph)
        dsd.type = self.identifier
        dsd.factoryGraph = graph
        return dsd

class _DataStructureDefinition(AnnotatibleTerms):
    component = predicate(SDMX.component)
    
class TimeSeries(Class):
    def __init__(self, graph=None):
        super(TimeSeries, self).__init__(SDMX.TimeSeries, graph=graph)
        self.label = Literal("time series", lang="en")
    def get(self, identifier=None, graph=None):
        if graph is None: graph=self.graph
        series = _Series(identifier=identifier, graph=graph)
        series.type = self.identifier
        series.factoryGraph = graph
        return series

class _Series(AnnotatibleTerms):
    def addDimension(self, dimension, value):
        self.graph.add((self.identifier, dimension, value))
    observation = predicate(SDMX.observation)
    dataSet = predicate(SDMX.dataSet)
    
class Observation(Class):
    def __init__(self, graph=None):
        super(Observation, self).__init__(SDMX.Observation, graph=graph)
        self.label = Literal("observed datum", lang="en")
    def get(self, identifier=None, graph=None):
        if graph is None: graph=self.graph
        obs = _Datum(identifier=identifier, graph=graph)
        obs.type = self.identifier
        obs.factoryGraph = graph
        return obs

class _Datum(AnnotatibleTerms):
    """
    An individual observation, obtained via :meth:`Observation.get`
    """
    def addValue(self, value, measure):
        self.graph.add((self.identifier, SDMX.obsValue, value))
        self.graph.add((self.identifier, SDMXATTR.unitMeasure, measure))
    def addDimension(self, dimension, value):
        self.graph.add((self.identifier, dimension, value))

class Dimension(Property):
    def __init__(self, graph):
        super(Dimension, self).__init__(SDMX.DimensionProperty, graph=graph)
        self.label = Literal("statistical dimension", lang="en")
        self.domain = TimeSeries(graph) | Observation(graph)

def rdf_data():
    graph = Graph(identifier=SDMX[""])
    ds = DataSet(graph)
    ts = TimeSeries(graph)
    obs = Observation(graph)
    dim = Dimension(graph)

    dataset = Property(SDMX["dataSet"], 
                       graph=graph)
    dataset.label = Literal("dataset", lang="en")
    dataset.domain = ts
    dataset.range = ds

    obsValue = Property(SDMX["obsValue"],
                        baseType = OWL.ObjectProperty,
                        graph=graph)
    obsValue.domain = obs

    yield graph

if __name__ == '__main__':
    for g in rdf_data():
        print g.serialize(format="n3")
