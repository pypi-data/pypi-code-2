"""
Changeset Tests
"""

from ordf.graph import Graph
from ordf.term import URIRef
from ordf.vocab.changeset import ChangeSet
from ordf.namespace import namespaces, RDF, CS
try:
    from rdflib.store.IOMemory import IOMemory
except ImportError:
    from rdflib.plugins.memory import IOMemory
from ordf.tests import our_test_graph, card_graph, identifier, nosep
import os

store = IOMemory()

def test_00_null():
    orig = our_test_graph()
    new = our_test_graph()

    ## make a changeset from nothing to our test data, and save
    cs = ChangeSet("test_cs", "Testing Fixtures")
    assert cs.diff(orig, new) == 0
    cs.commit()
    assert not cs

def test_01_create():
    orig = Graph(identifier=identifier)
    new = our_test_graph()

    ## make a changeset from nothing to our test data, and save
    cs = ChangeSet("test_cs", "Testing Fixtures")
    assert cs.diff(orig, new) == 85
    cs.commit()
    assert cs

def test_02_remove():
    ## create from empty
    orig = Graph(identifier=identifier)
    new = our_test_graph()
    cs = ChangeSet("test_cs", "Creating Graph", store=store)
    assert cs.diff(orig, new) == 85
    cs.commit()
    assert cs

    ## delete the data and check
    removed = our_test_graph()
    removed.remove((None, RDF.type, None))
    cs = ChangeSet("test_cs", "Removing Types", store=store)
    assert cs.diff(new, removed) == 18
    cs.commit()
    assert cs

    ## put the data back
    cs = ChangeSet("test_cs", "Adding Types Back", store=store)
    assert cs.diff(removed, our_test_graph()) == 18
    cs.commit()
    assert cs

def test_03_three():
    ## operations on three graphs in one changeset
    g1 = our_test_graph()
    g2 = card_graph()
    g3 = Graph(identifier="http://example.org/empty")
    g4 = Graph(identifier="http://example.org/empty")

    cs = ChangeSet("test_cs", "Delete test add card")
    assert cs.diff(g1, Graph(identifier=g1.identifier)) == 85
    assert cs.diff(Graph(identifier=g2.identifier), g2) == 61
    assert cs.diff(g3, g4) == 0
    cs.commit()

    changed = []
    for s,p,o in cs.triples((cs.identifier, CS.subjectOfChange, None)):
        changed.append(o)
    assert len(changed) == 2
