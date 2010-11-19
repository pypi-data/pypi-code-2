from ordf.namespace import RDF, DC, FOAF, OPMV
from ordf.graph import Graph, ConjunctiveGraph
from ordf.term import URIRef
from ordf.tests import fixture, identifier, card_graph
from ordf.vocab.foaf import Person

def test_10_bnc():
    g = fixture("marc.n3")
    proc = g.bnc((None, OPMV["wasGeneratedBy"], None))
    assert len(proc) == 10
    

def test_11_bnc():
    g = fixture("marc_bio.n3")
    subj = g.bnc((None, DC["subject"], None))
    assert len(subj) == 18
    

def test_12_replace():
    g = fixture("marc_bio.n3")
    subj = g.bnc((None, DC["subject"], None))
    repl = subj.replace((None, DC["subject"], None), (identifier, None, None))
    statements = list(repl.triples((identifier, None, None)))
    assert len(statements) == 4
