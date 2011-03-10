"""
.. autoclass:: Agent
"""

__all__ = ["Agent", "Person"]

from ordf.term import BNode, Literal, URIRef
from ordf.graph import Graph
from ordf.namespace import RDF, FOAF
from logging import getLogger
from hashlib import sha1

log = getLogger(__name__)

def rdf_data():
    log.info("Fetching %s" % FOAF)
    g = Graph(identifier=FOAF[""]).parse(FOAF)
    log.info("Parsed %s (%d triples)" % (FOAF, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.DLP.DLNormalization import NormalFormReduction
    foaf = handler.get(FOAF[""])
    if len(foaf) == 0:
        for foaf in rdf_data():
            handler.put(foaf)
    NormalFormReduction(foaf)
    return network.setupDescriptionLogicProgramming(foaf, addPDSemantics=False)    

class Agent(Graph):
    """
    .. autoattribute:: __types__
    .. autoattribute:: __rules__

    .. automethod:: nick
    .. automethod:: name
    .. automethod:: homepage
    """
    __types__ = [FOAF["Agent"]]
    "* *foaf:Agent*"
    __rules__ = [
        "{ ?a foaf:homepage ?u . ?b foaf:homepage ?u } => { ?a owl:sameAs ?b }"
        ]
    """
    * Inverse functional property *foaf:homepage* means if two things have 
      the same homepage then they are the same
    """
    def __init__(self, *av, **kw):
        super(Agent, self).__init__(*av, **kw)
        self.add((self.identifier, RDF["type"], FOAF["Agent"]))
    def nick(self, nick):
        """
        Set the *foaf:nick* on the present :class:`Graph`
        """
        self.add((self.identifier, FOAF["nick"], Literal(nick)))
    def name(self, name):
        """
        Set the *foaf:name* on the present :class:`Graph`
        """
        self.add((self.identifier, FOAF["name"], Literal(name)))
    def homepage(self, homepage):
        """
        Set the *foaf:homepage* on the present :class:`Graph`
        """
        self.add((self.identifier, FOAF["homepage"], URIRef(homepage)))
    def mbox(self, email):
        hash = sha1(email)
        self.add((self.identifier, FOAF["mbox_sha1sum"], Literal(hash.hexdigest())))

class Person(Agent):
    __types__ = [FOAF["Person"]]
