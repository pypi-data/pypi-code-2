__all__ = ["BNode", "Identifier", "Literal", "Node", "URIRef", "Variable"]

try:
    from rdflib.term import BNode as _BNode, Identifier, Literal, Node, URIRef, Variable
except ImportError:
    from rdflib import URIRef, BNode as _BNode, Literal, Variable
    from rdflib.Identifier import Identifier
    from rdflib.Node import Node

from time import time
from random import choice, seed
from string import ascii_letters, digits
seed(time())

class BNode(_BNode):
    def __new__(cls, value=None, *av, **kw):
        if value is None:
            value = "".join(choice(ascii_letters+digits) for x in range(8))
        return _BNode(value, *av, **kw)
