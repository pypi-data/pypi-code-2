"""
.. autoclass:: Graph

"""
__all__ = ["Graph", "ConjunctiveGraph", "ReadOnlyGraphAggregate"]

try:
    from rdflib.graph import Graph as _Graph
    from rdflib.graph import ReadOnlyGraphAggregate as _ROGraph
    from rdflib.graph import ConjunctiveGraph as _CGraph
    __rdflib_version__ = 3
except ImportError:
    from rdflib.Graph import Graph as _Graph
    from rdflib.Graph import ReadOnlyGraphAggregate as _ROGraph
    from rdflib.Graph import ConjunctiveGraph as _CGraph
    __rdflib_version__ = 2

### This is here because ordf/__init__.py is for the namespace package
### it is not really conceivable that any of the functions affected by
### this data get run without using ordf.graph
__import__("ordf.namespace", globals(), locals(), ["_init_ns"])._init_ns()
__import__("ordf.serializer") ## force registration of rdflib plugins

from ordf.namespace import bind_ns, RDF, RDFS, ORDF, RDFG
from ordf.term import BNode, Literal, URIRef, Node

class _Common(object):
    def bnc(self, triple, *av, **kw):
        """
        Return the BNode closure(s) for triples that are matched
        by the given "triple". Any additional positional or keyword
        arguments are passed to the constructor for the new graph.
        """
        result = Graph(*av, **kw)
        log = __import__("logging").getLogger(__name__)
        for s,p,o in self.triples(triple):
            result.add((s,p,o))
            if isinstance(o, BNode) and (o, None, None) not in result:
                result += self.bnc((o, None, None))
        return result

    def replace(self, old, new, *av, **kw):
        """
        Return a graph where triple "old" is replaced with triple
        "new". Any additional positional or keyword arguments are
        passed to the constructor for the new graph.
        """
        result = Graph(*av, **kw)
        result += self
        result.remove(old)
        ns, np, no = new
        for s,p,o in self.triples(old):
            if ns: s = ns
            if np: p = np
            if no: o = no
            result.add((s,p,o))
        return result

    def one(self, triple):
        """
        Return one matching "triple" or "None"
        """
        for statement in self.triples(triple):
            return statement

    def exists(self, triple):
        """
        Return "True" if "triple" exists, "False" otherwise
        """
        statement = self.one(triple)
        if statement is not None:
            return True
        return False

    def _distinct(self, func, *av, **kw):
        results = {}
        for x in func(*av, **kw):
            results[x] = True
        return results.keys()

    def distinct_subjects(self, *av, **kw):
        """
        Return a *distinct* set of subjects. Arguments are 
        as for :meth:subjects
        """
        return self._distinct(self.subjects, *av, **kw)

    def distinct_predicates(self, *av, **kw):
        """
        Return a *distinct* set of predicates. Arguments are 
        as for :meth:predicates
        """
        return self._distinct(self.predicates, *av, **kw)

    def distinct_objects(self, *av, **kw):
        """
        Return a *distinct* set of objects. Arguments are 
        as for :meth:objects
        """
        return self._distinct(self.objects, *av, **kw)

class Graph(_Graph, _Common):
    """
    A :class:`Graph` is a collection of *rdf:Statements*.

    This is the basic :class:`rdflib.graph.Graph` with a few added capabilities:

        * TODO: type and type implementation handling
        * bnode closures
        * handy helper methods :meth:`one` and :meth:`exists` and :meth:`distinct_*`
        * pointer to any :mod:`ordf.handler` in use.

    .. attribute:: identifier
    
    This is the URI of the resource that the graph can be said to be about.

    .. autoattribute:: __types__
    .. autoattribute:: __rules__

    .. attribute:: handler

        If the instance has been obtained via :mod:`ordf.handler`
        it will have the :attr:handler set to the handler that obtained it.

    .. automethod:: bnc
    .. automethod:: one
    .. automethod:: exists
    .. automethod:: replace
    .. automethod:: distinct_subjects
    .. automethod:: distinct_predicates
    .. automethod:: distinct_objects
    """
    
    __types__ = [RDFS["Resource"], RDFG["Graph"]]
    """
    Sub-classes should set this attribute to a list of :class:`URIRef`. It isn't
    necessary to copy data from parent classes. The basic :class:Graph has:

    * *rdfs:Resource*
    * *rdfg:Graph*
    """
    __rules__ = [
        "{ ?s ?p ?o } => { ?s a rdfs:Resource }"
        ]
    """
    Sub-classes should set this attribute to a list of inference relationships
    that are implicit in the nature of their *rdf:type*

    * everything is an *rdfs:Resource*
    """


    def __init__(self, store="IOMemory", identifier=None, **kw):
        if identifier is not None:
            if not isinstance(identifier, Node):
                identifier = URIRef(identifier)
        else:
            identifier = BNode()
        if __rdflib_version__ == 2:
            super(Graph, self).__init__(store, identifier)
        else:
            super(Graph, self).__init__(store=store, identifier=identifier)
        bind_ns(self)

    def version(self):
        version = None
        for s,p,version in self.triples((self.identifier, ORDF.changeSet, None)):
            break
        return version

class ConjunctiveGraph(_CGraph, _Common):
    __types__ = []
    def __init__(self, store="IOMemory", identifier=None, **kw):
        if __rdflib_version__ == 2:
            super(ConjunctiveGraph, self).__init__(store, identifier)
        else:
            super(ConjunctiveGraph, self).__init__(store=store, identifier=identifier, **kw)
        bind_ns(self)

class ReadOnlyGraphAggregate(_ROGraph, _Common):
    pass
