from ordf.tests import our_test_graph
from ordf.rdfobj import RDFObj
from ordf.term import URIRef
from ordf.namespace import *
from pprint import pprint

def test_rdfobj():
    obj = RDFObj(our_test_graph(), URIRef("urn:uuid:db531d1e-93df-46fe-a79f-f0fe4b99d7c4"))
#    pprint (obj)
#    pprint (obj[FRBR.creatorOf])
