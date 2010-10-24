from ordf.namespace import register_ns, Namespace
register_ns("ont", Namespace("http://www.example.org/ontology#"))
register_ns("data", Namespace("http://www.example.org/data#"))
from ordf.graph import Graph
from ordf.namespace import ONT, DATA, SKOS
from ordf.vocab.skos import ConceptScheme, Concept

class Food(ConceptScheme):
    def __init__(self, *av, **kw):
        super(Food, self).__init__(ONT.Food, *av, **kw)

class Fruit(Concept):
    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa["skipClassMembership"] = True
        super(Fruit, self).__init__(*av, **kwa)
        if not kw.get("skipClassMembership"):
            self.type = ONT.Fruit

class Veg(Concept):
    def __init__(self, *av, **kw):
        kwa = kw.copy()
        kwa["skipClassMembership"] = True
        super(Veg, self).__init__(*av, **kwa)
        if not kw.get("skipClassMembership"):
            self.type = ONT.Veg

def test_skos():
    ontology = Graph()
    data = Graph()

    food = Food(graph=ontology, factoryGraph=data)

    fruit = Concept(ONT.Fruit, graph=ontology, factoryGraph=data, factoryClass=Fruit)
    fruit.inScheme = food
    food.topConcept = fruit

    veg = Concept(ONT.Veg, graph=ontology, factoryGraph=data, factoryClass=Veg)
    veg.inScheme = food
    food.topConcept = veg

    apple = fruit.get_or_create(DATA.apple)
    apple.broader = fruit

    carrot = veg.get_or_create(DATA.carrot)
    carrot.broader = veg

    assert veg in carrot.broader
    assert fruit in apple.broader

    assert veg in food.topConcept
    assert food in veg.inScheme

    assert fruit in food.topConcept
    assert food in veg.inScheme
