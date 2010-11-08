from ordf.graph import Graph
from ordf.term import URIRef
import sys, os

identifier = URIRef("http://example.org/ordf/")
def our_test_graph():
    return fixture("test.rdf", identifier)

def card_graph():
    return fixture("card.rdf", URIRef("http://example.org/swh.rdf"))

def fixture(filename, identifier=None):
    curdir = os.path.dirname(__file__)
    datafile = os.path.join(curdir, "data", filename)
    g = Graph(identifier=identifier)
    g.parse(datafile, format="n3" if filename.endswith(".n3") else "xml")
    return g

def nosep(s):
    sys.stdout.write("%s... " % s)
    sys.stdout.flush()
