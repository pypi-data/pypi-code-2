__all__ = ["BNode", "Identifier", "Literal", "Node", "URIRef", "Variable"]

try:
    from rdflib.term import BNode, Identifier, Literal, Node, URIRef, Variable
except ImportError:
    from rdflib import URIRef, Literal, BNode, Variable
    from rdflib.Identifier import Identifier
    from rdflib.Node import Node
