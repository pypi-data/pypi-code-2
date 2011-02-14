from ordf.graph import Graph
from ordf.handler import init_handler
from ordf.namespace import register_ns, Namespace, RDF, RDFS, FOAF, OWL, SKOS
from ordf.term import Literal
from ordf.vocab.owl import Class

def fuxi_handler(default={}):
    config = {
        "ordf.readers": "fuxi,rdflib",
        "ordf.writers": "fuxi,rdflib",
        }
    config.update(default)
    return init_handler(config)

EX = Namespace("http://example.org/")
register_ns("ex", EX)

def test_01_rdfs():
    h = fuxi_handler({ "fuxi.args": "ordf.vocab.rdfs" })

    g = Graph(identifier=EX["Max"])
    g.add((EX["Max"], RDF["type"], EX["Cat"]))
    h.put(g)
    
    r = h.get(EX["Max"])
    assert r.exists((EX["Max"], RDF["type"], RDFS["Resource"]))

def test_02_owl():
    h = fuxi_handler({ "fuxi.args": "ordf.vocab.owl" })

    ctx = h.context("test", "cat")

    cat = Class(EX["Cat"], graph=Graph(identifier=EX["Cat"]))
    ctx.add(cat.graph)

    cateq = Class(EX["CatEquiv"],
                  equivalentClass=[EX["Cat"]],
                  graph=Graph(identifier=EX["CatEquiv"]))
    ctx.add(cateq.graph)

    max = Graph(identifier=EX["Max"])
    max.add((EX["Max"], RDF["type"], EX["Cat"]))
    ctx.add(max)

    ctx.commit()

    cat = h.get(EX["Cat"])
    assert cat.exists((EX["Cat"], OWL["equivalentClass"], EX["CatEquiv"]))

def test_03_skos():
    h = fuxi_handler({ "fuxi.args": "ordf.vocab.skos" })
    ctx = h.context("test", "cat")

    animal = Class(EX["Animal"], graph=Graph(identifier=EX["Animal"]))
    animal.graph.add((EX["Animal"], RDF["type"], SKOS["Concept"]))
    ctx.add(animal.graph)

    cat = Class(EX["Cat"], graph=Graph(identifier=EX["Cat"]))
    cat.graph.add((EX["Cat"], SKOS["broaderTransitive"], EX["Animal"]))
    ctx.add(cat.graph)

    tabby = Class(EX["Tabby"], graph=Graph(identifier=EX["Tabby"]))
    tabby.graph.add((EX["Tabby"], SKOS["broaderTransitive"], EX["Cat"]))
    ctx.add(tabby.graph)

    ctx.commit()

    animal = h.get(EX["Animal"])
    assert animal.exists((EX["Animal"], SKOS["narrowerTransitive"], EX["Cat"]))
    assert animal.exists((EX["Animal"], SKOS["narrowerTransitive"], EX["Tabby"]))

def test_04_retract():
    print
    h = fuxi_handler({ "fuxi.args": "ordf.vocab.rdfs" })
    ctx = h.context("test", "retract")
    
    max = Graph(identifier=EX["Max"])
    max.add((EX["Max"], RDF["type"], EX["Cat"]))
    ctx.add(max)
    cs = ctx.commit()

    max = h.get(EX["Max"]) ## should contain inferred triples
    assert max.exists((EX["Max"], RDF["type"], RDFS["Resource"]))

    ## empty the rule sets, would not normally be done so
    ## no public API for this, really
    h.fuxi.rule_modules = []
    del h.fuxi.network

    max.add((EX["Max"], FOAF["name"], Literal("Max")))
    ctx = h.context("test", "retract")
    ctx.add(max)
    cs = ctx.commit()

    max = h.get(EX["Max"]) ## should not contain inferred triples
    assert not max.exists((EX["Max"], RDF["type"], RDFS["Resource"]))
