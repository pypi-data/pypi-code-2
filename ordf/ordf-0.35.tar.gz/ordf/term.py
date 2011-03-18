__all__ = ["BNode", "Identifier", "Literal", "Node", "URIRef", "Variable"]

try:
    from rdflib.term import BNode, Identifier, Literal, Node, URIRef, Variable
except ImportError:
    from rdflib import URIRef, BNode, Literal, Variable
    from rdflib.Identifier import Identifier
    from rdflib.Node import Node
