#
# examples from the manual
#

from ordf.namespace import register_ns, Namespace
register_ns("ex", Namespace("http://example.org/"))

## imports required for the example
from ordf.graph import Graph
from ordf.namespace import EX, FOAF, RDFS
from ordf.term import URIRef, Literal
from ordf.vocab.owl import Class, AnnotatibleTerms, predicate, object_predicate

class Person(AnnotatibleTerms):
    def __init__(self, *av, **kw):
        super(Person, self).__init__(*av, **kw)
        self.type = FOAF.Person
    name = predicate(FOAF.name)
    homepage = predicate(FOAF.homepage)

def test_00_person():
    ## create a person
    bob = Person(EX.bob)
    bob.name = "Bob"
    bob.homepage = URIRef("http://example.org/")

    assert FOAF.Person in bob.type
    assert "Bob" in bob.name
    assert "http://example.org/" in bob.homepage

class Country(AnnotatibleTerms):
    def __init__(self, *av, **kw):
        super(Country, self).__init__(*av, **kw)
        self.type = EX.Country

class City(AnnotatibleTerms):
    def __init__(self, *av, **kw):
        super(City, self).__init__(*av, **kw)
        self.type = EX.City
    country = object_predicate(EX.country, Country)

def test_01_obj_pred():
    data = Graph()

    scotland = Country(EX.Scotland, graph=data)
    scotland.label = "Scotland"
    
    edinburgh = City(EX.Edinburgh, graph=data)
    edinburgh.label = "Edinburgh"
    edinburgh.country = scotland

    assert scotland in edinburgh.country

class PlaceClass(Class):
    def __init__(self, **kw):
        super(PlaceClass, self).__init__(EX.Place, **kw)

class CountryClass(Class):
    def __init__(self, **kw):
        super(CountryClass, self).__init__(EX.Country, **kw)
        self.subClassOf = PlaceClass(graph=self.graph, factoryGraph=self.factoryGraph)
        self.factoryClass = Country
        self.label = "Country"

class CityClass(Class):
    def __init__(self, **kw):
        super(CityClass, self).__init__(EX.City, **kw)
        self.subClassOf = PlaceClass(graph=self.graph, factoryGraph=self.factoryGraph)
        self.factoryClass = City
        self.label = "City"

def test_02_class():
    ontology = Graph()
    data = Graph()

    scotland = Country(EX.scotland, graph=data)
    scotland.label = "Scotland"
    
    edinburgh = City(EX.edinburgh, graph=data)
    edinburgh.label = "Edinburgh"
    edinburgh.country = scotland

    country = CountryClass(graph=ontology, factoryGraph=data)
    city = CityClass(graph=ontology, factoryGraph=data)

    assert country.get(EX.scotland) == scotland
    assert city.get(EX.edinburgh) == edinburgh

def test_03_filter():
    from telescope import v

    ontology = Graph()
    data = Graph()

    country = CountryClass(graph=ontology, factoryGraph=data)
    city = CityClass(graph=ontology, factoryGraph=data)

    scotland = Country(EX.scotland, graph=data)
    scotland.label = "Scotland"
    russia = Country(EX.russia, graph=data)
    russia.label = "Russia"

    results = list(country.filter((v.id, RDFS.label, Literal("Russia"))))
    assert len(results) == 1
    assert 'Russia' in results[0].label
