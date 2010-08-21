from ordf.vocab.fresnel import Fresnel
from ordf.tests import fixture
from sys import stdout
from xml.dom import minidom

def lens():
    g = fixture("lens.n3")
    return Fresnel(store=g.store, identifier=g.identifier)

def test_01_lens():
    l = lens()
    g = fixture("marc_bio.n3")
    styles, doc = l.format(g)
    print minidom.parseString(doc).toprettyxml()
