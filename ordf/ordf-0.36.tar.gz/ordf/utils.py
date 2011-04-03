"""
Miscellaneous Utilities
=======================

.. autofunction:: get_identifier
.. autofunction:: uuid
"""

__all__ = ["uuid", "get_identifier"]

from uuid import uuid1, uuid3, NAMESPACE_URL
from ordf.graph import _Graph
from ordf.term import URIRef

def uuid(uri):
    """
    Convenience method - if the argument starts with *urn:uuid:*
    does nothing. Otherwise constructs a *urn:uuid:* form URI from
    the given argument. Uses the :func:`uuid.uuid3` function from the
    standard Python library
    """
    identifier = get_identifier(uri)
    if identifier.startswith("urn:uuid:"):
        return identifier
    return u"urn:uuid:" + unicode(uuid3(NAMESPACE_URL, identifier.encode("ascii")))

def get_identifier(g):
    """
    Returns a :class:`~rdflib.term.URIRef` for the argument which may be an 
    instance of :class:`~rdflib.graph.Graph` or a string. If it is already a
    :class:`~rdflib.term.URIRef` (which itself is a subclass of unicode string)
    it simply returns it.
    """
    if isinstance(g, _Graph):
        return g.identifier
    if isinstance(g, URIRef):
        return g
    return URIRef(g)

