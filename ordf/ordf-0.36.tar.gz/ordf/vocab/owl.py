#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Overview of InfixOWL
--------------------

The core OWL abstract syntax is implemented based on this recipe:

    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/384122

Quoting the original InfixOWL docstrings,

    Python has the wonderful "in" operator and it would be nice
    to have additional infix operator like this. This recipe shows
    how (almost) arbitrary infix operators can be defined.

Some usage examples follow below.

>>> from ordf.namespace import register_ns
>>> exNs = Namespace("http://example.com/")
>>> register_ns("ex", exNs)
>>> g = Graph()

Now we have an empty graph, we can construct OWL classes in it
using the Python classes defined in this module

>>> a = Class(exNs.Opera,graph=g)

Now we can assert rdfs:subClassOf and owl:equivalentClass relationships 
(in the underlying graph) with other classes using the 'subClassOf' 
and 'equivalentClass' descriptors which can be set to a list
of objects for the corresponding predicates.

>>> a.subClassOf = [exNs.MusicalWork]

We can then access the rdfs:subClassOf relationships

>>> print list(a.subClassOf)
[Class: ex:MusicalWork ]

This can also be used against already populated graphs:

.. code-block:: python

    owlGraph = Graph().parse(OWL)
    namespace_manager.bind('owl', OWL, override=False)
    owlGraph.namespace_manager = namespace_manager
    list(Class(OWL.Class,graph=owlGraph).subClassOf)

    --> [Class: rdfs:Class ]

Operators are also available.  For instance we can add ex:Opera to the extension
of the ex:CreativeWork class via the '+=' operator

>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork
>>> b = Class(exNs.CreativeWork,graph=g)
>>> b += a
>>> list(a.subClassOf)
[Class: ex:CreativeWork , Class: ex:MusicalWork ]

And we can then remove it from the extension as well

>>> b -= a
>>> a
Class: ex:Opera SubClassOf: ex:MusicalWork

Boolean class constructions can also  be created with Python operators
For example, The | operator can be used to construct a class consisting of a owl:unionOf 
the operands:

>>> c =  a | b | Class(exNs.Work,graph=g)
>>> c
( ex:Opera or ex:CreativeWork or ex:Work )

Boolean class expressions can also be operated as lists (using python list operators)

>>> del c[c.index(Class(exNs.Work,graph=g))]
>>> c
( ex:Opera or ex:CreativeWork )

The '&' operator can be used to construct class intersection:
      
>>> woman = Class(exNs.Female,graph=g) & Class(exNs.Human,graph=g)
>>> woman.identifier = exNs.Woman
>>> woman
( ex:Female and ex:Human )
>>> len(woman)
2

Enumerated classes can also be manipulated

>>> contList = [Class(exNs.Africa,graph=g),Class(exNs.NorthAmerica,graph=g)]
>>> EnumeratedClass(members=contList,graph=g)
{ ex:Africa ex:NorthAmerica }

owl:Restrictions can also be instanciated:

>>> Restriction(exNs.hasParent,graph=g,allValuesFrom=exNs.Human)
( ex:hasParent only ex:Human )

Restrictions can also be created using Manchester OWL syntax in 'colloquial' Python 

>>> exNs.hasParent |some| Class(exNs.Physician,graph=g)
( ex:hasParent some ex:Physician )
>>> Property(exNs.hasParent,graph=g) |max| Literal(1)
( ex:hasParent max 1 )

Datatype and Object Properties
------------------------------

.. autoclass:: predicate
    :show-inheritance:
.. autoclass:: object_predicate
    :show-inheritance:
.. autoclass:: cached_predicate
    :show-inheritance:
.. autoclass:: cached_object_predicate
    :show-inheritance:

Core classes
------------

.. autoclass:: Individual
.. autoclass:: AnnotatibleTerms
    :show-inheritance:
.. autoclass:: Ontology
    :show-inheritance:
.. autoclass:: Class
    :show-inheritance:
.. autoclass:: Property
    :show-inheritance:
"""
import os, itertools
from pprint import pprint

from ordf.collection import Collection
from ordf.graph import Graph
from ordf.namespace import bind_ns, Namespace, OWL, RDF, RDFS, XSD
from ordf.term import Node, BNode, Identifier, Literal, URIRef, Variable

from rdflib.util import first

##
## Data fixtures for ORDF
##
def rdf_data():
    from logging import getLogger
    log = getLogger(__name__)
    graph_uri = OWL[""][:-1]
    log.info("Fetching %s" % graph_uri)
    g = Graph(identifier=graph_uri).parse(graph_uri)
    log.info("Parsed %s (%d triples)" % (graph_uri, len(g)))
    yield g

def inference_rules(handler, network):
    from FuXi.Horn.HornRules import HornFromN3
    import os, pkg_resources
    rule_file = pkg_resources.resource_filename("ordf.vocab", os.path.join("n3", "owl-rules.n3"))
    rules = HornFromN3(rule_file)
    for rule in rules:
        network.buildNetworkFromClause(rule)
    
    owl = handler.get(OWL[""][:-1])
    if len(owl) == 0:
        for owl in rdf_data():
            pass
    dlp = network.setupDescriptionLogicProgramming(owl, addPDSemantics=True)
    return list(rules) + dlp

# attribute properties
class predicate(property):
    """
    This function provides facilities that look a bit like the properties
    on a `Django`_ or `SQLAlchemy`_ class.

    .. _Django: http://www.djangoproject.com/
    .. _SQLAlchemy: http://www.sqlalchemy.org/

    It is used when you make a subclass of :class:`Individual` or one
    of its subclasses so that you can put properties on. Here is an 
    example taken from the :mod:`ordf.vocab.foaf` module:

    >>> from ordf.namespace import FOAF
    >>> class Person(Class):
    ...     name = predicate(FOAF.name)
    ...
    >>> norman = Person()
    >>> norman.name = Literal("Norman Bethune")
    >>> [str(x) for x in norman.name]
    ['Norman Bethune']
    >>> norman.name = [Literal('Bob Smith')]
    >>> [str(x) for x in norman.name]
    ['Bob Smith']
    >>> del norman.name
    >>> len(list(norman.name))
    0

    The *set()* operation can take either a literal or a list/tuple
    of literals.
    """
    def __init__(self, term):
        self.term = term
        super(predicate, self).__init__(self._get, self._set, self._del)
    def _get(self, obj):
        return obj.graph.distinct_objects(obj.identifier, self.term)
    def _set(self, obj, value):
        if not value: return
        if not isinstance(value, list) and not isinstance(value, tuple):
            value = (value,)
        else:
            obj.graph.remove((obj.identifier, self.term, None))
        for x in value:
            if hasattr(x, "identifier") and isinstance(x.identifier, Node):
                x = x.identifier
            elif not isinstance(x, Node):
                x = Literal(x)
            obj.graph.add((obj.identifier, self.term, x))
    def _del(self, obj):
        obj.graph.remove((obj.identifier, self.term, None))

class object_predicate(predicate):
    """
    This function behaves similarly to :class:`predicate` except that
    rather than returning the term associated with the predicate it
    will attempt to return an instantiated Individual (or subclass
    thereof). In this way such a predicate will behave somewhat like
    a foreign key relationship as implemented in SQL ORMs.

    >>> from ordf.namespace import Namespace
    >>> EX = Namespace("http://example.org/")
    >>> class Country(Class):
    ...     pass
    ...
    >>> class Province(Class):
    ...     country = object_predicate(EX.country, Country)
    ...
    >>> canada = Country(EX.canada)
    >>> canada.label = "Canada"
    >>> quebec = Province(EX.quebec, graph=canada.graph)
    >>> quebec.label = "Québec"
    >>> quebec.country = canada
    >>> for country in quebec.country: print [str(x) for x in country.label]
    ['Canada']

    Try out some support for strings in place of class names for
    self-referential classes.

    >>> from ordf.namespace import FOAF
    >>> class Person(Class):
    ...     knows = object_predicate(FOAF.knows, "Person", globals())
    ...
    >>> bob = Person(EX.bob)
    >>> alice = Person(EX.alice)
    >>> bob.knows = alice
    >>> [type(x) for x in bob.knows]
    [<class 'ordf.vocab.owl.Person'>]
    """
    def __init__(self, term, implementation=None, globals=None):
        if implementation is None:
            self._cls = Individual
        if isinstance(implementation, basestring):
            self._cls = implementation
            self._globals = globals
        else:
            assert issubclass(implementation, Individual), "expected an Individual, got an %s" % implementation
            self._cls = implementation
        super(object_predicate, self).__init__(term)

    def _get(self, obj):
        if isinstance(self._cls, basestring):
            self._cls = self._globals[self._cls]
        for identifier in super(object_predicate, self)._get(obj):
            yield self._cls(identifier, graph=obj.graph, factoryGraph=obj.factoryGraph, 
                            skipClassMembership=True)

class cached_predicate(predicate):
    """
    This version of the :class:`predicate` function behaves the
    same way except that with *get()* operations the returned values
    are cached. Doing a *set()* or *del()* operation causes the cache
    to be cleared. Usage is essentially identical.

    >>> from ordf.namespace import DC
    >>> class Book(Class):
    ...    title = cached_predicate(DC.subject)
    ...
    >>> we = Book()
    >>> we.title = (Literal("We", lang="en"), Literal("Nous", lang="fr"))
    >>> [str(x) for x in we.title]
    ['We', 'Nous']
    >>> ### prove that the value is cached
    >>> we.graph.remove((we.identifier, None, None))
    >>> len(list(we.title))
    2
    >>> del we.title
    >>> len(list(we.title))
    0
    """
    def _cache(self, obj):
        if not hasattr(obj, "__predicate_cache__"):
            obj.__predicate_cache__ = {}
        return obj.__predicate_cache__
    def _get(self, obj):
        _cache = self._cache(obj)
        if self.term in _cache:
            return _cache[self.term]
        results = list(super(cached_predicate, self)._get(obj))
        _cache[self.term] = results
        return results
    def _set(self, obj, value):
        super(cached_predicate, self)._set(obj, value)
        _cache = self._cache(obj)
        if self.term in _cache: del _cache[self.term]
    def _del(self, obj):
        super(cached_predicate, self)._del(obj)
        _cache = self._cache(obj)
        if self.term in _cache: del _cache[self.term]

class cached_object_predicate(cached_predicate):
    """
    And the caching analogue to :class:`object_predicate`.

    >>> from ordf.namespace import Namespace
    >>> EX = Namespace("http://example.org/")
    >>> class Cat(Class):
    ...     pass
    >>> class Person(Class):
    ...     pet = cached_object_predicate(EX.pet, Cat)
    ...
    >>> bob = Person(EX.bob)
    >>> bob.label = "Bob"
    >>> max = Cat(EX.max, graph=bob.graph)
    >>> max.label = "Max"
    >>> bob.pet = max
    >>> for pet in bob.pet: print [str(x) for x in pet.label]
    ['Max']
    >>> # prove the data has been cached
    >>> bob.graph.remove((bob.identifier, None, None))
    >>> for pet in bob.pet: print [str(x) for x in pet.label]
    ['Max']
    >>> # prove that it is the *same* object
    >>> for pet in bob.pet:
    ...     assert id(pet) == id(max)
    ...
    """
    def __init__(self, term, implementation=None, globals=None):
        if implementation is None:
            self._cls = Individual
        elif isinstance(implementation, basestring):
            self._cls = implementation
            self._globals = globals
        else:
            assert issubclass(implementation, Individual), "expected an Individual, got an %s" % implementation
            self._cls = implementation
        super(cached_object_predicate, self).__init__(term)

    def _set(self, obj, value):
        if not isinstance(value, list) and not isinstance(value, tuple):
            value = [value]
        cached_values = self._get(obj)
        for x in value:
            if isinstance(x, URIRef) or isinstance(x, BNode):
                x = self._cls(value, graph=obj.graph)
            assert isinstance(x, Individual), "expected an Individual, got an %s" % x
            if x not in cached_values:
                cached_values.append(x)
                obj.graph.add((obj.identifier, self.term, x.identifier))

    def _get(self, obj):
        if isinstance(self._cls, basestring):
            self._cls = self._globals[self._cls]
        _cache = self._cache(obj)
        if self.term in _cache:
            return _cache[self.term]
        results = [
            self._cls(x, graph=obj.graph, factoryGraph=obj.factorGraph,
                      skipClassMembership=True)
            for x in super(cached_object_predicate, self)._get(obj)
            ]
        _cache[self.term] = results
        return results

# definition of an Infix operator class
# this recipe also works in jython
# calling sequence for the infix is either:
#  x |op| y
# or:
# x <<op>> y

class Infix(object):
    def __init__(self, function):
        self.function = function
    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __or__(self, other):
        return self.function(other)
    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))
    def __rshift__(self, other):
        return self.function(other)
    def __call__(self, value1, value2):
        return self.function(value1, value2)

def generateQName(graph,uri):
    prefix,uri,localName = graph.compute_qname(classOrIdentifier(uri)) 
    return u':'.join([prefix,localName])    

def classOrTerm(thing):
    if isinstance(thing,Class):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode,Literal))
        return thing

def classOrIdentifier(thing):
    if isinstance(thing,(Property,Class)):
        return thing.identifier
    else:
        assert isinstance(thing,(URIRef,BNode)),"Expecting a Class, Property, URIRef, or BNode.. not a %s"%thing
        return thing

def propertyOrIdentifier(thing):
    if isinstance(thing,Property):
        return thing.identifier
    else:
        assert isinstance(thing,URIRef)
        return thing

def manchesterSyntax(thing,store,boolean=None,transientList=False):
    """
    Core serialization
    """
    assert thing is not None
    if boolean:
        if transientList:
            liveChildren=iter(thing)
            children = [manchesterSyntax(child,store) for child in thing ]
        else:
            liveChildren=iter(Collection(store,thing))
            children = [manchesterSyntax(child,store) for child in Collection(store,thing)]
        if boolean == OWL.intersectionOf:
            childList=[]
            named = []
            for child in liveChildren:
                if isinstance(child,URIRef):
                    named.append(child)
                else:
                    childList.append(child)
            if named:
                def castToQName(x):
                    prefix,uri,localName = store.compute_qname(x) 
                    return u':'.join([prefix,localName])
                
                if len(named) > 1:
                    prefix = '( '+ ' and '.join(map(castToQName,named)) + ' )'                
                else:
                    prefix = manchesterSyntax(named[0],store)
                if childList:
                    return prefix+ ' that '+' and '.join(
                             map(lambda x:manchesterSyntax(x,store),childList))
                else:
                    return prefix
            else:
                return '( '+ ' and '.join(children) + ' )'
        elif boolean == OWL.unionOf:
            return '( '+ ' or '.join(children) + ' )'
        elif boolean == OWL.oneOf:
            return '{ '+ ' '.join(children) +' }'
        else:            
            assert boolean == OWL.complementOf
    elif OWL.Restriction in store.objects(subject=thing, predicate=RDF.type):
        prop = list(store.objects(subject=thing, predicate=OWL.onProperty))[0]
        prefix,uri,localName = store.compute_qname(prop)
        propString = u':'.join([prefix,localName])
        for onlyClass in store.objects(subject=thing, predicate=OWL.allValuesFrom):
            return '( %s only %s )'%(propString,manchesterSyntax(onlyClass,store))
        for val in store.objects(subject=thing, predicate=OWL.hasValue):
            return '( %s value %s )'%(propString,manchesterSyntax(val,store))        
        for someClass in store.objects(subject=thing, predicate=OWL.someValuesFrom):    
            return '( %s some %s )'%(propString,manchesterSyntax(someClass,store))
        cardLookup = {OWL.maxCardinality:'max',OWL.minCardinality:'min',OWL.cardinality:'equals'}
        for s,p,o in store.triples_choices((thing,cardLookup.keys(),None)):            
            return '( %s %s %s )'%(propString,cardLookup[p],o.encode('utf-8'))
    compl = list(store.objects(subject=thing, predicate=OWL.complementOf)) 
    if compl:
        return '( not %s )'%(manchesterSyntax(compl[0],store))
    else:
        for boolProp,col in store.query("SELECT ?p ?bool WHERE { ?class a owl:Class; ?p ?bool . ?bool rdf:first ?foo }",
                                         initBindings={Variable("?class"):thing},
                                         initNs={ "owl": OWL, "rdf": RDF }):
            if not isinstance(thing,URIRef):                
                return manchesterSyntax(col,store,boolean=boolProp)
        try:
            prefix,uri,localName = store.compute_qname(thing) 
            qname = u':'.join([prefix,localName])
        except Exception,e:
            if isinstance(thing,BNode):
                return thing.n3()
            return "<"+thing+">"
            print list(store.objects(subject=thing,predicate=RDF.type))
            raise
            return '[]'#+thing._id.encode('utf-8')+'</em>'            
        label=first(Class(thing,graph=store).label)
        if label:
            return label.encode('utf-8')
        else:
            return qname.encode('utf-8')

def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type,object=OWL.Class):
        if isinstance(c,URIRef):
            yield Class(c)

def termDeletionDecorator(prop):
    def someFunc(func):
        func.property = prop
        return func
    return someFunc

class TermDeletionHelper:
    def __init__(self, prop):
        self.prop = prop
    def __call__(self, f):
        def _remover(inst):
            inst.graph.remove((inst.identifier,self.prop,None))
        return _remover

class Individual(object):
    """
    A typed individual, the base class of the InfixOWL classes.
    
    :param identifier:
        The identifier for this individual, a :class:`ordf.term.URIRef`

    :param graph:
        The graph which will provide the backing store for the individual.
        If *None* a new graph will be created.

    .. attribute:: identifier

        The identifier attribute is handled specially to make it 
        immutable.

    .. attribute:: graph

        The graph acting as a backing store is always accessible via
        this attribute on instances of :class:`Individual`

    .. attribute:: factoryGraph

        The usual practice is to set this equal to the :attr:`graph` 
        attribute, it is the source of data used by :meth:`serialize`

    .. attribute:: type

        Type is essentially the result of using the :func:`predicate` 
        function with *rdf:type*

    .. attribute:: cached_types

        A cached version of the :attr:`type` attribute.

    .. attribute:: sameAs

        Conceptually similar with *owl:sameAs* but special handling is
        required since it will return a full instance of a subclass of
        :class:`Individual`.

    .. automethod:: clearInDegree
    .. automethod:: clearOutDegree
    .. automethod:: delete
    .. automethod:: replace
    .. automethod:: serialize
    """
    def __init__(self, identifier=None, graph=None, factoryGraph=None, **kw):
        self.__identifier = identifier is not None and identifier or BNode()
        if factoryGraph is not None:
            self.factoryGraph = factoryGraph
        if graph is None:
            self.graph = self.factoryGraph
        else:
            self.graph = graph    
        self.qname = None
        if not isinstance(self.identifier,BNode):
            try:
                prefix,uri,localName = self.graph.compute_qname(self.identifier) 
                self.qname = u':'.join([prefix,localName])
            except:
                pass
    
    factoryGraph = Graph()
    def serialize(self, graph):
        """
        Take terms related to this individual using a blank node
        closure and add them to the provided graph.
        """
        graph += self.factoryGraph.bnc((self.identifier,None,None))

    def clearInDegree(self):
        """
        Remove references to this individual as an object in the
        backing store.
        """
        self.graph.remove((None,None,self.identifier))    

    def clearOutDegree(self):
        """
        Remove all statements to this individual as a subject in the
        backing store. Note that this only removes the statements 
        themselves, not the blank node closure so there is a chance
        that this will cause orphaned blank nodes to remain in the 
        graph.
        """
        self.graph.remove((self.identifier,None,None))    

    def delete(self):
        """
        Delete the individual from the graph, clearing the in and
        out degrees.
        """
        self.clearInDegree()
        self.clearOutDegree()
        
    def replace(self,other):
        """
        Replace the individual in the graph with the given other,
        causing all triples that refer to it to be changed and then
        delete the individual.
        """
        for s,p,o in self.graph.triples((None,None,self.identifier)):
            self.graph.add((s,p,classOrIdentifier(other)))
        self.delete()
    
    def _get_identifier(self):
        return self.__identifier
    def _set_identifier(self, i):
        assert i
        if i != self.__identifier:
            oldStmtsOut = [(p,o) for s,p,o in self.graph.triples((self.__identifier,None,None))]
            oldStmtsIn  = [(s,p) for s,p,o in self.graph.triples((None,None,self.__identifier))]
            for p1,o1 in oldStmtsOut:                
                self.graph.remove((self.__identifier,p1,o1))
            for s1,p1 in oldStmtsIn:                
                self.graph.remove((s1,p1,self.__identifier))
            self.__identifier = i
            self.graph.addN([(i,p1,o1,self.graph) for p1,o1 in oldStmtsOut])
            self.graph.addN([(s1,p1,i,self.graph) for s1,p1 in oldStmtsIn])
        if not isinstance(i,BNode):
            try:
                prefix,uri,localName = self.graph.compute_qname(i) 
                self.qname = u':'.join([prefix,localName])
            except:
                pass

    def __eq__(self, other):
        assert isinstance(other,Individual), repr(other)
        return self.identifier == other.identifier
            
    identifier = property(_get_identifier, _set_identifier)
    type = predicate(RDF.type)
    cached_types = cached_predicate(RDF.type)
    sameAs = predicate(OWL.sameAs)
    
class AnnotatibleTerms(Individual):
    """
    Terms in an OWL ontology with rdfs:label and rdfs:comment

    .. attribute:: isDefinedBy

        The result of calling the :func:`predicate` function on
        *rdfs:isDefinedBy*

    .. attribute:: label

        Similarly for *rdfs:label*

    .. attribute:: comment

        Similarly for *rdfs:comment*

    .. attribute:: seeAlso

        Similarly for *rdfs:seeAlso*
    """
    label = predicate(RDFS.label)
    comment = predicate(RDFS.comment)
    seeAlso = predicate(RDFS.seeAlso)
    isDefinedBy = predicate(RDFS.isDefinedBy)


class Ontology(AnnotatibleTerms):
    """
    The owl ontology metadata

    .. attribute:: versionInfo

        The result of calling :func:`predicate` on *owl:versionInfo*

    .. attribute:: imports

        Ditto with *owl:imports*
    """
    def __init__(self, identifier=None, imports=None, comment=None,graph=None):
        super(Ontology, self).__init__(identifier,graph)
        self.imports = imports and imports or []
        self.comment = comment and comment or []
        if (self.identifier,RDF.type,OWL.Ontology) not in self.graph:
            self.type = OWL.Ontology
    versionInfo = predicate(OWL.versionInfo)
    imports = predicate(OWL.imports)

def AllClasses(graph):
    prevClasses=set()
    for c in graph.subjects(predicate=RDF.type,object=OWL.Class):
        if c not in prevClasses:
            prevClasses.add(c)
            yield Class(c)            

def AllProperties(graph):
    prevProps=set()
    for s,p,o in graph.triples_choices(
               (None,RDF.type,[OWL.Symmetric,
                               OWL.FunctionalProperty,
                               OWL.InverseFunctionalProperty,
                               OWL.TransitiveProperty,
                               OWL.DatatypeProperty,
                               OWL.ObjectProperty])):
        if o in [OWL.Symmetric,
                 OWL.InverseFunctionalProperty,
                 OWL.TransitiveProperty,
                 OWL.ObjectProperty]:
            bType=OWL.ObjectProperty
        else:
            bType=OWL.DatatypeProperty
        if s not in prevProps:
            prevProps.add(s)
            yield Property(s,
                           graph=graph,
                           baseType=bType)            
    
class ClassNamespaceFactory(Namespace):
    def term(self, name):
        return Class(URIRef(self + name))

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"): # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)    
    
def DeepClassClear(classToPrune):
    """
    Recursively clear the given class, continuing
    where any related class is an anonymous class
    
    >>> g = Graph()    
    >>> EX = Namespace("http://example.com/")
    >>> bind_ns(g, { "ex": EX })
    >>> Individual.factoryGraph = g
    >>> classB = Class(EX.B)
    >>> classC = Class(EX.C)
    >>> classD = Class(EX.D)
    >>> classE = Class(EX.E)
    >>> classF = Class(EX.F)
    >>> anonClass = EX.someProp|some|classD
    >>> classF += anonClass
    >>> list(anonClass.subClassOf)
    [Class: ex:F ]
    >>> classA = classE | classF | anonClass    
    >>> classB += classA
    >>> classA.equivalentClass = [Class()]
    >>> classB.subClassOf = [EX.someProp|some|classC]
    >>> classA
    ( ex:E or ex:F or ( ex:someProp some ex:D ) )
    >>> DeepClassClear(classA)
    >>> classA
    (  )
    >>> list(anonClass.subClassOf)
    []
    >>> classB
    Class: ex:B SubClassOf: ( ex:someProp some ex:C )
    
    >>> otherClass = classD | anonClass
    >>> otherClass
    ( ex:D or ( ex:someProp some ex:D ) )
    >>> DeepClassClear(otherClass)
    >>> otherClass
    (  )
    >>> otherClass.delete()
    >>> list(g.triples((otherClass.identifier,None,None)))
    []
    """
    def deepClearIfBNode(_class):
        if isinstance(classOrIdentifier(_class),BNode):
            DeepClassClear(_class)
    classToPrune=CastClass(classToPrune,Individual.factoryGraph)
    for c in classToPrune.subClassOf:
        deepClearIfBNode(c)
    classToPrune.graph.remove((classToPrune.identifier,RDFS.subClassOf,None))
    for c in classToPrune.equivalentClass:
        deepClearIfBNode(c)
    classToPrune.graph.remove((classToPrune.identifier,OWL.equivalentClass,None))
    inverseClass = classToPrune.complementOf
    if inverseClass:
        classToPrune.graph.remove((classToPrune.identifier,OWL.complementOf,None))
        deepClearIfBNode(inverseClass)
    if isinstance(classToPrune,BooleanClass):
        for c in classToPrune:
            deepClearIfBNode(c)
        classToPrune.clear()
        classToPrune.graph.remove((classToPrune.identifier,
                          classToPrune._operator,
                          None))    
        
class MalformedClass(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __repr__(self): 
        return self.msg       
    
def CastClass(c,graph=None):
    graph = graph is None and c.factoryGraph or graph
    for kind in graph.objects(subject=classOrIdentifier(c),
                              predicate=RDF.type):
        if kind == OWL.Restriction:
            kwArgs = {'identifier':classOrIdentifier(c),
                      'graph'     :graph}
            for s,p,o in graph.triples((classOrIdentifier(c),
                                        None,
                                        None)):
                if p != RDF.type:
                    if p == OWL.onProperty:
                        kwArgs['onProperty'] = o
                    else:
                        if p not in Restriction.restrictionKinds:
                            continue
                        kwArgs[str(p.split(OWL)[-1])] = o
            if not set([str(i.split(OWL)[-1]) for i in Restriction.restrictionKinds]).intersection(kwArgs):
                raise MalformedClass("Malformed owl:Restriction")
            return Restriction(**kwArgs)
        else:
            for s,p,o in graph.triples_choices((classOrIdentifier(c),
                                                [OWL.intersectionOf,
                                                 OWL.unionOf,
                                                 OWL.oneOf],
                                                None)):
                if p == OWL.oneOf:
                    return EnumeratedClass(classOrIdentifier(c),graph=graph)
                else:
                    return BooleanClass(classOrIdentifier(c),operator=p,graph=graph)
            #assert (classOrIdentifier(c),RDF.type,OWL.Class) in graph
            return Class(classOrIdentifier(c),graph=graph,skipClassMembership=True)
    
class Class(AnnotatibleTerms):
    """
    'General form' for classes:
    
    The Manchester Syntax (supported in Protege) is used as the basis for the form 
    of this class
    
    See: http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf::
    
        Class: classID {Annotation
            ( (SubClassOf: ClassExpression)
              | (EquivalentTo ClassExpression)
              | (DisjointWith ClassExpression)) }
    
    Appropriate excerpts from OWL Reference:
    
        ".. Subclass axioms provide us with partial definitions: they represent 
        necessary but not sufficient conditions for establishing class 
        membership of an individual."
     
        ".. A class axiom may contain (multiple) owl:equivalentClass statements"   
        
        "..A class axiom may also contain (multiple) owl:disjointWith statements.."
    
        "..An owl:complementOf property links a class to precisely one class 
        description."

    .. automethod:: get
    .. automethod:: get_or_create
    .. automethod:: query
    .. automethod:: filter
    """
    def _serialize(self,graph):
        for cl in self.subClassOf:
            CastClass(cl,self.graph).serialize(graph)
        for cl in self.equivalentClass:
            CastClass(cl,self.graph).serialize(graph)
        for cl in self.disjointWith:
            CastClass(cl,self.graph).serialize(graph)
        if self.complementOf:
            CastClass(self.complementOf,self.graph).serialize(graph)
        
    def serialize(self,graph):
        for fact in self.graph.triples((self.identifier,None,None)):
            graph.add(fact)
        self._serialize(graph)
    
    def __init__(self, identifier=None, graph=None, factoryGraph=None, factoryClass=Individual,
                 subClassOf=None,equivalentClass=None,
                 disjointWith=None,complementOf=None,
                 skipClassMembership=False,
                 comment=None):
        super(Class, self).__init__(identifier, graph=graph, factoryGraph=factoryGraph)
        if not skipClassMembership and (self.identifier,RDF.type,OWL.Class) not in self.graph and \
           (self.identifier,RDF.type,OWL.Restriction) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL.Class))
        self.factoryClass    = factoryClass
        self.subClassOf      = subClassOf and subClassOf or [] 
        self.equivalentClass = equivalentClass and equivalentClass or []
        self.disjointWith    = disjointWith  and disjointWith or []
        if complementOf:
            self.complementOf    = complementOf
        self.comment = comment and comment or []
        
    def _get_extent(self,graph=None):
        for member in (graph is None and self.graph or graph).subjects(predicate=RDF.type,
                                          object=self.identifier):
            yield member
    def _set_extent(self,other):
        if not other:
            return
        for m in other:
            self.graph.add((classOrIdentifier(m),RDF.type,self.identifier))
    @TermDeletionHelper(RDF.type)
    def _del_type(self):            
        pass            
    extent = property(_get_extent, _set_extent, _del_type)            

    def _get_extentQuery(self):
        return (Variable('CLASS'),RDF.type,self.identifier)
    def _set_extentQuery(self,other): pass
    extentQuery = property(_get_extentQuery, _set_extentQuery)            

    def get(self, identifier):
        """
        Simple and naive individual retrieval from the factory graph.
        Raises a KeyError if no individual with type of the present
        class is found in the factory graph.

        >>> EX=Namespace("http://example.org/")
        >>> class Country(AnnotatibleTerms):
        ...     def __init__(self, *av, **kw):
        ...         super(Country, self).__init__(*av, **kw)
        ...         self.type = EX.Country
        ...
        >>> class CountryClass(Class):
        ...     def __init__(self, **kw):
        ...         super(CountryClass, self).__init__(EX.Country, factoryClass=Country)
        ...
        >>> country = CountryClass()
        >>> kenya = Country(EX.kenya)
        >>> kenya.label = "Kenya"
        >>> [str(x) for x in country.get(EX.kenya).label]
        ['Kenya']
        >>> country.get(EX.uganda)
        Traceback (most recent call last):
          raise KeyError("no individual %s with type %s" % (identifier, self.identifier))
        KeyError: u'no individual http://example.org/uganda with type http://example.org/Country'
        """
        if self.factoryGraph.exists((identifier, RDF.type, self.identifier)):
            return self.factoryClass(identifier, graph=self.factoryGraph)
        raise KeyError("no individual %s with type %s" % (identifier, self.identifier))

    def get_or_create(self, identifier):
        """
        Similar to the :meth:`get` except that it will not raise a key error
        and will create the individual requested.
        """
        return self.factoryClass(identifier, graph=self.factoryGraph)

    def query(self, *where):
        """
        Return a Telescope Select object that will query for individuals
        with the RDF type of the present class and additional where
        statements as provided.

        >>> from telescope import v
        >>> c = Class(URIRef("http://example.org/"))
        >>> print c.query((v.id, RDFS.label, Literal("Russia"))).compile()
        SELECT DISTINCT ?id
        WHERE { ?id <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://example.org/> . ?id <http://www.w3.org/2000/01/rdf-schema#label> "Russia" }
        """
        from telescope import Select, v
        q = Select([v.id], distinct=True).where(
            (v.id, RDF.type, self.identifier)
            ).where(*where)
        return q

    def filter(self, *where):
        """
        Return individuals that match the given query. The query will
        be constructed via :meth:`query`
        """
        q = self.query(*where)
        for identifier in self.factoryGraph.query(q.compile()):
            yield self.factoryClass(identifier, graph=self.factoryGraph)
            
    def __hash__(self):
        """
        >>> b=Class(OWL.Restriction)
        >>> c=Class(OWL.Restriction)
        >>> len(set([b,c]))
        1
        """
        return hash(self.identifier)

    def __eq__(self, other):
        assert isinstance(other,Class),repr(other)
        return self.identifier == other.identifier
    
    def __iadd__(self, other):
        assert isinstance(other,Class)
        other.subClassOf = [self]
        return self

    def __isub__(self, other):
        assert isinstance(other,Class)
        self.graph.remove((classOrIdentifier(other),RDFS.subClassOf,self.identifier))
        return self
    
    def __invert__(self):
        """
        Shorthand for Manchester syntax's not operator
        """
        return Class(complementOf=self)

    def __or__(self,other):
        """
        Construct an anonymous class description consisting of the union of this class and '
        other' and return it
        """
        return BooleanClass(operator=OWL.unionOf,members=[self,other],graph=self.graph)

    def __and__(self,other):
        """
        Construct an anonymous class description consisting of the intersection of this class and '
        other' and return it
        
        Chaining 3 intersections
        
        >>> g = Graph()    
        >>> exNs = Namespace("http://example.com/")
        >>> bind_ns(g, { "ex": exNs })
        >>> female      = Class(exNs.Female,graph=g)
        >>> human       = Class(exNs.Human,graph=g)
        >>> youngPerson = Class(exNs.YoungPerson,graph=g)
        >>> youngWoman = female & human & youngPerson
        >>> youngWoman
        ex:YoungPerson that ( ex:Female and ex:Human )
        >>> isinstance(youngWoman,BooleanClass)
        True
        >>> isinstance(youngWoman.identifier,BNode)
        True
        """
        return BooleanClass(operator=OWL.intersectionOf,members=[self,other],graph=self.graph)

    class _subClassOf(object_predicate):
        def __init__(self):
            class _xClass(Individual):
                def __new__(self, *av, **kw):
                    kwa=kw.copy()
                    kwa["skipClassMembership"] = True
                    return Class(*av, **kwa)
            super(self.__class__, self).__init__(RDFS.subClassOf, _xClass)
    subClassOf = _subClassOf()

    class _classPredicate(object_predicate):
        def __init__(self, term):
            class _xClass(Individual):
                def __new__(self, *av, **kw):
                    return Class(*av, **kw)
            super(self.__class__, self).__init__(term, _xClass)

    equivalentClass = _classPredicate(OWL.equivalentClass)
    disjointWith = _classPredicate(OWL.disjointWith)

    class _complement(object_predicate):
        def __init__(self):
            class _xClass(Individual):
                def __new__(self, *av, **kw):
                    return Class(*av, **kw)
            super(self.__class__, self).__init__(OWL.complementOf, _xClass)
        def _get(self, obj):
            comp = list(super(self.__class__, self)._get(obj))
            if not comp:
                return None
            elif len(comp) == 1:
                return Class(comp[0],graph=self.graph)
            else:
                raise Exception(len(comp))
    complementOf = _complement()

    def isPrimitive(self):
        if (self.identifier,RDF.type,OWL.Restriction) in self.graph:
            return False
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL.intersectionOf,
                                                                OWL.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        for e in ec:
            return False
        if self.complementOf:
            return False
        return True
    
    def subSumpteeIds(self):
        for s in self.graph.subjects(predicate=RDFS.subClassOf,object=self.identifier):
            yield s
        
#    def __iter__(self):
#        for s in self.graph.subjects(predicate=RDFS.subClassOf,object=self.identifier):
#            yield Class(s,skipClassMembership=True)
    
    def __repr__(self,full=False,normalization=True):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        exprs = []
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass,p,rdfList in self.graph.triples_choices((self.identifier,
                                                               [OWL.intersectionOf,
                                                                OWL.unionOf],
                                                                None)):
            ec.append(manchesterSyntax(rdfList,self.graph,boolean=p))
        dc = list(self.disjointWith)
        c  = self.complementOf
        if c:
            dc.append(c)
        klassKind = ''
        label = list(self.graph.objects(self.identifier,RDFS.label))
        label = label and '('+label[0]+')' or ''
        if sc:
            if full:
                scJoin = '\n                '
            else:
                scJoin = ', '
            necStatements = [
              isinstance(s,Class) and isinstance(self.identifier,BNode) and
                                      repr(CastClass(s,self.graph)) or
                                      #repr(BooleanClass(classOrIdentifier(s),
                                      #                  operator=None,
                                      #                  graph=self.graph)) or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in sc]
            if necStatements:
                klassKind = "Primitive Type %s"%label
            exprs.append("SubClassOf: %s"%scJoin.join(necStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if ec:
            nec_SuffStatements = [    
              isinstance(s,basestring) and s or 
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in ec]
            if nec_SuffStatements:
                klassKind = "A Defined Class %s"%label
            exprs.append("EquivalentTo: %s"%', '.join(nec_SuffStatements))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        if dc:
            exprs.append("DisjointWith %s\n"%'\n                 '.join([
              manchesterSyntax(classOrIdentifier(s),self.graph) for s in dc]))
            if full:
                exprs[-1]="\n    "+exprs[-1]
        descr = list(self.graph.objects(self.identifier,RDFS.comment))
        if full and normalization:
            klassDescr = klassKind and '\n    ## %s ##'%klassKind +\
            (descr and "\n    %s"%descr[0] or '') + ' . '.join(exprs) or ' . '.join(exprs)
        else:
            klassDescr = full and (descr and "\n    %s"%descr[0] or '') or '' + ' . '.join(exprs)
        return (isinstance(self.identifier,BNode) and "Some Class " or "Class: %s "%self.qname)+klassDescr

class OWLRDFListProxy(object):
    def __init__(self,rdfList,members=None):
        members = members and members or []
        if rdfList:
            self._rdfList = Collection(self.graph,rdfList[0])
            for member in members:
                if member not in self._rdfList:
                    self._rdfList.append(classOrIdentifier(member))
        else:
            self._rdfList = Collection(self.graph,BNode(),
                                       [classOrIdentifier(m) for m in members])
            self.graph.add((self.identifier,self._operator,self._rdfList.uri)) 
            
    def __eq__(self, other):
        """
        Equivalence of boolean class constructors is determined by equivalence of its
        members 
        """
        assert isinstance(other,Class),repr(other)+repr(type(other))
        if isinstance(other,BooleanClass):
            length = len(self)
            if length != len(other):
                return False
            else:
                for idx in range(length):
                    if self[idx] != other[idx]:
                        return False
                    return True
        else:
            return self.identifier == other.identifier

    #Redirect python list accessors to the underlying Collection instance
    def __len__(self):
        return len(self._rdfList)

    def index(self, item):
        return self._rdfList.index(classOrIdentifier(item))
    
    def __getitem__(self, key):
        return self._rdfList[key]

    def __setitem__(self, key, value):
        self._rdfList[key] = classOrIdentifier(value)
        
    def __delitem__(self, key):
        del self._rdfList[key]    
        
    def clear(self):
        self._rdfList.clear()    

    def __iter__(self):
        for item in self._rdfList:
            yield item

    def __contains__(self, item):
        for i in self._rdfList:
            if i == classOrIdentifier(item):
                return 1
        return 0
    
    def append(self, item):
        self._rdfList.append(item)    

    def __iadd__(self, other):
        self._rdfList.append(classOrIdentifier(other))
        return self

class EnumeratedClass(OWLRDFListProxy,Class):
    """
    Class for owl:oneOf forms:
    
    OWL Abstract Syntax is used
    
    axiom ::= 'EnumeratedClass(' classID ['Deprecated'] { annotation } { individualID } ')'
    
    >>> g = Graph()    
    >>> exNs = Namespace("http://example.com/")
    >>> bind_ns(g, { "ex": exNs })
    >>> Individual.factoryGraph = g
    >>> ogbujiBros = EnumeratedClass(exNs.ogbujicBros,
    ...                              members=[exNs.chime,
    ...                                       exNs.uche,
    ...                                       exNs.ejike])
    >>> ogbujiBros
    { ex:chime ex:uche ex:ejike }
    >>> print g.serialize(format='n3')
    <BLANKLINE>
    @prefix ex: <http://example.com/>.
    @prefix owl: <http://www.w3.org/2002/07/owl#>.
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
    <BLANKLINE>
     ex:ogbujicBros a owl:Class;
         owl:oneOf ( ex:chime ex:uche ex:ejike ). 
    <BLANKLINE>
     ex:chime a owl:Class. 
    <BLANKLINE>
     ex:ejike a owl:Class. 
    <BLANKLINE>
     ex:uche a owl:Class. 
    """
    _operator = OWL.oneOf
    def isPrimitive(self):
        return False
    def __init__(self, identifier=None,members=None,graph=None):
        Class.__init__(self,identifier,graph = graph)
        members = members and members or []
        rdfList = list(self.graph.objects(predicate=OWL.oneOf,subject=self.identifier))
        OWLRDFListProxy.__init__(self, rdfList, members)
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)        
    
    def serialize(self,graph):
        clonedList = Collection(graph,BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)
        
        graph.add((self.identifier,self._operator,clonedList.uri))
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            if p != self._operator:
                graph.add((s,p,o))
        self._serialize(graph)
    
BooleanPredicates = [OWL.intersectionOf,OWL.unionOf]

class BooleanClassExtentHelper:
    """
    >>> testGraph = Graph()
    >>> Individual.factoryGraph = testGraph
    >>> EX = Namespace("http://example.com/")
    >>> bind_ns(testGraph, { "ex": EX })
    >>> fire  = Class(EX.Fire)
    >>> water = Class(EX.Water) 
    >>> testClass = BooleanClass(members=[fire,water])
    >>> testClass2 = BooleanClass(operator=OWL.unionOf,members=[fire,water])
    >>> for c in BooleanClass.getIntersections():
    ...     print c
    ( ex:Fire and ex:Water )
    >>> for c in BooleanClass.getUnions():
    ...     print c
    ( ex:Fire or ex:Water )
    """    
    def __init__(self, operator):
        self.operator = operator
    def __call__(self, f):
        def _getExtent():
            for c in Individual.factoryGraph.subjects(self.operator):
                yield BooleanClass(c,operator=self.operator)            
        return _getExtent
    
class Callable:
    def __init__(self, anycallable):
        self.__call__ = anycallable    

class BooleanClass(OWLRDFListProxy,Class):
    """
    See: http://www.w3.org/TR/owl-ref/#Boolean
    
    owl:complementOf is an attribute of Class, however
    
    """
    @BooleanClassExtentHelper(OWL.intersectionOf)
    @Callable
    def getIntersections(): pass
    getIntersections = Callable(getIntersections)    

    @BooleanClassExtentHelper(OWL.unionOf)
    @Callable
    def getUnions(): pass
    getUnions = Callable(getUnions)    
            
    def __init__(self,identifier=None,operator=OWL.intersectionOf,
                 members=None,graph=None):
        if operator is None:
            props=[]
            for s,p,o in graph.triples_choices((identifier,
                                                [OWL.intersectionOf,
                                                 OWL.unionOf],
                                                 None)):
                props.append(p)
                operator = p
            assert len(props)==1,repr(props)
        Class.__init__(self,identifier,graph = graph)
        assert operator in [OWL.intersectionOf,OWL.unionOf], str(operator)
        self._operator = operator
        rdfList = list(self.graph.objects(predicate=operator,subject=self.identifier))
        assert not members or not rdfList,"This is a previous boolean class description!"+repr(Collection(self.graph,rdfList[0]).n3())        
        OWLRDFListProxy.__init__(self, rdfList, members)

    def serialize(self,graph):
        clonedList = Collection(graph,BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)
        
        graph.add((self.identifier,self._operator,clonedList.uri))
        
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            if p != self._operator:
                graph.add((s,p,o))
        self._serialize(graph)

    def isPrimitive(self):
        return False

    def changeOperator(self,newOperator):
        """
        Converts a unionOf / intersectionOf class expression into one 
        that instead uses the given operator
        
        >>> testGraph = Graph()
        >>> Individual.factoryGraph = testGraph
        >>> EX = Namespace("http://example.com/")
        >>> bind_ns(testGraph, { "ex": EX })
        >>> fire  = Class(EX.Fire)
        >>> water = Class(EX.Water) 
        >>> testClass = BooleanClass(members=[fire,water])
        >>> testClass
        ( ex:Fire and ex:Water )
        >>> testClass.changeOperator(OWL.unionOf)
        >>> testClass
        ( ex:Fire or ex:Water )
        >>> try: testClass.changeOperator(OWL.unionOf)
        ... except Exception, e: print e
        The new operator is already being used!
        
        """
        assert newOperator != self._operator,"The new operator is already being used!"
        self.graph.remove((self.identifier,self._operator,self._rdfList.uri))
        self.graph.add((self.identifier,newOperator,self._rdfList.uri))
        self._operator = newOperator

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(self._rdfList.uri,self.graph,boolean=self._operator)

    def __or__(self,other):
        """
        Adds other to the list and returns self
        """
        assert self._operator == OWL.unionOf
        self._rdfList.append(classOrIdentifier(other))
        return self

def AllDifferent(members):
    """
    DisjointClasses(' description description { description } ')'
    
    """
    pass

class Restriction(Class):
    """
    restriction ::= 'restriction(' datavaluedPropertyID dataRestrictionComponent 
                                 { dataRestrictionComponent } ')'
                  | 'restriction(' individualvaluedPropertyID 
                      individualRestrictionComponent 
                      { individualRestrictionComponent } ')'    
    """
    
    restrictionKinds = [OWL.allValuesFrom,
                        OWL.someValuesFrom,
                        OWL.hasValue,
                        OWL.maxCardinality,
                        OWL.minCardinality]
    
    def __init__(self,
                 onProperty,
                 graph = Graph(),
                 allValuesFrom=None,
                 someValuesFrom=None,
                 value=None,
                 cardinality=None,
                 maxCardinality=None,
                 minCardinality=None,
                 identifier=None):
        super(Restriction, self).__init__(identifier,
                                          graph=graph,
                                          skipClassMembership=True)
        if (self.identifier,
            OWL.onProperty,
            propertyOrIdentifier(onProperty)) not in graph:
            graph.add((self.identifier,OWL.onProperty,propertyOrIdentifier(onProperty)))
        self.onProperty = onProperty
        restrTypes = [
                      (allValuesFrom,OWL.allValuesFrom ),
                      (someValuesFrom,OWL.someValuesFrom),
                      (value,OWL.hasValue),
                      (cardinality,OWL.cardinality),
                      (maxCardinality,OWL.maxCardinality),
                      (minCardinality,OWL.minCardinality)]
        validRestrProps = [(i,oTerm) for (i,oTerm) in restrTypes if i] 
        assert len(validRestrProps)
        restrictionRange,restrictionType = validRestrProps.pop()
        self.restrictionType = restrictionType
        if isinstance(restrictionRange,Identifier):
            self.restrictionRange = restrictionRange
        elif isinstance(restrictionRange,Class):
            self.restrictionRange = classOrIdentifier(restrictionRange)
        else:
            self.restrictionRange = first(self.graph.objects(self.identifier,
                                                             restrictionType))
        if (self.identifier,
            restrictionType,
            self.restrictionRange) not in self.graph:
            self.graph.add((self.identifier,restrictionType,self.restrictionRange))
        assert self.restrictionRange is not None,Class(self.identifier)
        if (self.identifier,RDF.type,OWL.Restriction) not in self.graph:
            self.graph.add((self.identifier,RDF.type,OWL.Restriction))
            self.graph.remove((self.identifier,RDF.type,OWL.Class))

    def serialize(self,graph):
        Property(self.onProperty,graph=self.graph).serialize(graph)
        for s,p,o in self.graph.triples((self.identifier,None,None)):
            graph.add((s,p,o))
            if p in [OWL.allValuesFrom,OWL.someValuesFrom]:
                CastClass(o, self.graph).serialize(graph)

    def isPrimitive(self):
        return False

    def __hash__(self):
        return hash((self.onProperty,self.restrictionRange))

    def __eq__(self, other):
        """
        Equivalence of restrictions is determined by equivalence of the property 
        in question and the restriction 'range'
        """
        assert isinstance(other,Class),repr(other)+repr(type(other))
        if isinstance(other,Restriction):
            return other.onProperty == self.onProperty and \
                   other.restrictionRange == self.restrictionRange
        else:
            return False

    def _get_onProperty(self):
        return list(self.graph.objects(subject=self.identifier,predicate=OWL.onProperty))[0]
    def _set_onProperty(self, prop):
        triple = (self.identifier,OWL.onProperty,propertyOrIdentifier(prop))
        if not prop:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.onProperty)
    def _del_onProperty(self):            
        pass            
                        
    onProperty = property(_get_onProperty, _set_onProperty, _del_onProperty)

    def _get_allValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.allValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_allValuesFrom(self, other):
        triple = (self.identifier,OWL.allValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.allValuesFrom)
    def _del_allValuesFrom(self):            
        pass            
                        
    allValuesFrom = property(_get_allValuesFrom, _set_allValuesFrom, _del_allValuesFrom)

    def _get_someValuesFrom(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.someValuesFrom):
            return Class(i,graph=self.graph)
        return None
    def _set_someValuesFrom(self, other):
        triple = (self.identifier,OWL.someValuesFrom,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.someValuesFrom)
    def _del_someValuesFrom(self):            
        pass            
                        
    someValuesFrom = property(_get_someValuesFrom, _set_someValuesFrom, _del_someValuesFrom)

    def _get_hasValue(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.hasValue):
            return Class(i,graph=self.graph)
        return None
    def _set_hasValue(self, other):
        triple = (self.identifier,OWL.hasValue,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.hasValue)
    def _del_hasValue(self):            
        pass            
                        
    hasValue = property(_get_hasValue, _set_hasValue, _del_hasValue)

    def _get_cardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.cardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_cardinality(self, other):
        triple = (self.identifier,OWL.cardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.cardinality)
    def _del_cardinality(self):            
        pass            
                        
    cardinality = property(_get_cardinality, _set_cardinality, _del_cardinality)

    def _get_maxCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.maxCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_maxCardinality(self, other):
        triple = (self.identifier,OWL.maxCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.maxCardinality)
    def _del_maxCardinality(self):            
        pass            
                        
    maxCardinality = property(_get_maxCardinality, _set_maxCardinality, _del_maxCardinality)

    def _get_minCardinality(self):
        for i in self.graph.objects(subject=self.identifier,predicate=OWL.minCardinality):
            return Class(i,graph=self.graph)
        return None
    def _set_minCardinality(self, other):
        triple = (self.identifier,OWL.minCardinality,classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)
            
    @TermDeletionHelper(OWL.minCardinality)
    def _del_minCardinality(self):            
        pass            
                        
    minCardinality = property(_get_minCardinality, _set_minCardinality, _del_minCardinality)

    def restrictionKind(self):
        for p in self.graph.triple_choices((self.identifier,
                                            self.restrictionKinds,
                                            None)):
            return p.split(OWL)[-1]
        raise
            
    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this restriction
        """
        return manchesterSyntax(self.identifier,self.graph)

### Infix Operators ###

some     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,someValuesFrom=_class))
only     = Infix(lambda prop,_class: Restriction(prop,graph=_class.graph,allValuesFrom=_class))
max      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,maxCardinality=_class))
min      = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,minCardinality=_class))
exactly  = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,cardinality=_class))
value    = Infix(lambda prop,_class: Restriction(prop,graph=prop.graph,value=_class))

PropertyAbstractSyntax=\
"""
%s( %s { %s } 
%s
{ 'super(' datavaluedPropertyID ')'} ['Functional']
{ domain( %s ) } { range( %s ) } )"""

class Property(AnnotatibleTerms):
    """
    What is a property?::

        axiom ::= 'DatatypeProperty(' datavaluedPropertyID ['Deprecated'] { annotation } 
                    { 'super(' datavaluedPropertyID ')'} ['Functional']
                    { 'domain(' description ')' } { 'range(' dataRange ')' } ')'
                | 'ObjectProperty(' individualvaluedPropertyID ['Deprecated'] { annotation } 
                    { 'super(' individualvaluedPropertyID ')' }
                    [ 'inverseOf(' individualvaluedPropertyID ')' ] [ 'Symmetric' ] 
                    [ 'Functional' | 'InverseFunctional' | 'Functional' 'InverseFunctional' |
                      'Transitive' ]
                    { 'domain(' description ')' } { 'range(' description ')' } ')    
    """
    def __init__(self,identifier=None,graph = None,baseType=OWL.ObjectProperty,
                      subPropertyOf=None,domain=None,range=None,inverseOf=None,
                      otherType=None,equivalentProperty=None,comment=None):
        super(Property, self).__init__(identifier,graph)
        assert not isinstance(self.identifier,BNode)
        if (self.identifier,RDF.type,baseType) not in self.graph:
            self.graph.add((self.identifier,RDF.type,baseType))
        self._baseType=baseType
        self.subPropertyOf = subPropertyOf
        self.inverseOf     = inverseOf
        self.domain        = domain
        self.range         = range
        self.comment = comment and comment or []

    def serialize(self,graph):
        for fact in self.graph.triples((self.identifier,None,None)):
            graph.add(fact)
        for p in itertools.chain(self.subPropertyOf,
                                 self.inverseOf):
            p.serialize(graph)
        for c in itertools.chain(self.domain,
                                 self.range):
            CastClass(c,self.graph).serialize(graph)

    def _get_extent(self,graph=None):
        for triple in (graph is None and 
                       self.graph or graph).triples((None,self.identifier,None)):
            yield triple
    def _set_extent(self,other):
        if not other:
            return
        for subj,obj in other:
            self.graph.add((subj,self.identifier,obj))
            
    extent = property(_get_extent, _set_extent)            

    def __repr__(self):
        rt=[]
        if OWL.ObjectProperty in self.type:
            rt.append(u'ObjectProperty( %s annotation(%s)'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))
            if first(self.inverseOf):
                twoLinkInverse=first(first(self.inverseOf).inverseOf)
                if twoLinkInverse and twoLinkInverse.identifier == self.identifier:
                    inverseRepr=first(self.inverseOf).qname
                else:
                    inverseRepr=repr(first(self.inverseOf))
                rt.append(u"  inverseOf( %s )%s"%(inverseRepr,
                            OWL.Symmetric in self.type and u' Symmetric' or u''))
            for s,p,roleType in self.graph.triples_choices((self.identifier,
                                                            RDF.type,
                                                            [OWL.Functional,
                                                             OWL.InverseFunctionalProperty,
                                                             OWL.Transitive])):
                rt.append(unicode(roleType.split(OWL)[-1]))
        else:
            rt.append('DatatypeProperty( %s %s'\
                       %(self.qname,first(self.comment) and first(self.comment) or ''))            
            for s,p,roleType in self.graph.triples((self.identifier,
                                                    RDF.type,
                                                    OWL.Functional)):
                rt.append(u'   Functional')
        def canonicalName(term,g):
            normalizedName=classOrIdentifier(term)
            if isinstance(normalizedName,BNode):
                return term
            elif normalizedName.startswith(XSD):
                return unicode(term)
            elif first(g.triples_choices((
                      normalizedName,
                      [OWL.unionOf,
                       OWL.intersectionOf],None))):
                return repr(term)
            else:
                return unicode(term.qname)
        rt.append(u' '.join([u"   super( %s )"%canonicalName(superP,self.graph) 
                              for superP in self.subPropertyOf]))                        
        rt.append(u' '.join([u"   domain( %s )"% canonicalName(domain,self.graph) 
                              for domain in self.domain]))
        rt.append(u' '.join([u"   range( %s )"%canonicalName(range,self.graph) 
                              for range in self.range]))
        rt=u'\n'.join([expr for expr in rt if expr])
        rt+=u'\n)'
        return unicode(rt).encode('utf-8')
                    
    def _get_subPropertyOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=RDFS.subPropertyOf):
            yield Property(anc,graph=self.graph)
    def _set_subPropertyOf(self, other):
        if not other:
            return        
        for sP in other:
            self.graph.add((self.identifier,RDFS.subPropertyOf,classOrIdentifier(sP)))
            
    @TermDeletionHelper(RDFS.subPropertyOf)
    def _del_subPropertyOf(self):            
        pass            
                        
    subPropertyOf = property(_get_subPropertyOf, _set_subPropertyOf, _del_subPropertyOf)

    def _get_inverseOf(self):
        for anc in self.graph.objects(subject=self.identifier,predicate=OWL.inverseOf):
            yield Property(anc,graph=self.graph)
    def _set_inverseOf(self, other):
        if not other:
            return        
        self.graph.add((self.identifier,OWL.inverseOf,classOrIdentifier(other)))
        
    @TermDeletionHelper(OWL.inverseOf)
    def _del_inverseOf(self):            
        pass            
                
    inverseOf = property(_get_inverseOf, _set_inverseOf, _del_inverseOf)

    def _get_domain(self):
        for dom in self.graph.objects(subject=self.identifier,predicate=RDFS.domain):
            yield Class(dom,graph=self.graph)
    def _set_domain(self, other):
        if not other:
            return
        if isinstance(other,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(other)))
        else:
            for dom in other:
                self.graph.add((self.identifier,RDFS.domain,classOrIdentifier(dom)))
                
    @TermDeletionHelper(RDFS.domain)
    def _del_domain(self):            
        pass            
                                
    domain = property(_get_domain, _set_domain, _del_domain)

    def _get_range(self):
        for ran in self.graph.objects(subject=self.identifier,predicate=RDFS.range):
            yield Class(ran,graph=self.graph)
    def _set_range(self, ranges):
        if not ranges:
            return
        if isinstance(ranges,(Individual,Identifier)):
            self.graph.add((self.identifier,RDFS.range,classOrIdentifier(ranges)))
        else:        
            for range in ranges:
                self.graph.add((self.identifier,RDFS.range,classOrIdentifier(range)))
                
    @TermDeletionHelper(RDFS.range)
    def _del_range(self):            
        pass            
                                
    range = property(_get_range, _set_range, _del_range)

        
def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
