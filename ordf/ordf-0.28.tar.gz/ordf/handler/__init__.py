"""
This is the operational core of ORDF. In the normal course of events, an
application will,

    1. Instantiate a :class:`Handler` object, which is usually a singleton.
    2. Register one or more handler implementations for reading or writing.
    3. Use the :meth:`get` and :meth:`put` methods to respectively retrieve
       and save *Graphs*.
    4. Use :meth:`context` to save *Graphs* within the context of a
       :class:`ordf.vocab.changeset.ChangeSet`.

See the documentation for :class:`HandlerPlugin` for how handler
the implementation works.

Initialising Handlers
---------------------

.. autoclass:: ConfigError
.. autofunction:: init_handler

Reading and Writing Graphs -- :class:`Handler`
----------------------------------------------

.. autoclass:: Handler

Base for Storage and Indices -- :class:`HandlerPlugin`
------------------------------------------------------

.. autoclass:: HandlerPlugin

Making Changesets -- :class:`ChangeContext`
-------------------------------------------

.. autoclass:: ChangeContext
"""
__all__ = ["Handler", "HandlerPlugin", "init_handler", "ConfigError"]

from ordf.vocab.changeset import ChangeSet
from ordf.graph import Graph, _Graph, ConjunctiveGraph, _CGraph
from ordf.namespace import namespaces, CS, RDF
import pkg_resources
import logging

class ChangeContext(object):
    """
    Takes care of constructing changesets and distributes the results

    Not to be instantiated directly. Returned from the :meth:`Handler.context`
    method.
    
    Typical usage:

    .. code-block:: python

        ctx = handler.context(...)
        ctx.add(graph)
        ctx.add(another)
        ctx.commit()

    .. automethod:: add
    .. automethod:: commit
    .. automethod:: rollback
    """
    def __init__(self, handler, *av, **kw):
        self.handler = handler
        self.__av__ = av
        self.__kw__ = kw
        self.graphs = []
        self.rollback()

    def add(self, graph):
        """
        Add an RDFLib Graph instance to this changeset context
        """
        copy = Graph(identifier=graph.identifier, store=self.store)
        for statement in graph.triples((None, None, None)):
            copy.add(statement)
        self.graphs.append(copy)

    def commit(self):
        """
        Commit any pending changes in this context and distribute
        them via the handler.

        This method actually constructs the :class:`ordf.changeset.ChangeSet`
        instance. This *ChangeSet* is initialised with any positional and 
        keyword arguments that were passed to the present class on creation.

        It then iterates over any graphs that have been added with 
        :meth:add and requests the previous version from the
        :meth:`Handler.get`. The differences between the previous and current
        versions are added to the changeset.

        Now, *ChangeSet* in hand, we call the :meth:`Handler.put` for the
        changeset and then for each of the new versions of the graphs in
        turn.
        """
	kw = self.__kw__.copy()
	kw["store"] = self.store
        cs = ChangeSet(*self.__av__, **kw)

        ## we keep track if there is already a changeset in the store
        embedded_changeset = False
        for graph in self.graphs:
            ## check if is changeset.
            ## do not diff changesets
            is_changeset = False
            for s,p,o in graph.triples((graph.identifier, RDF.type, CS.ChangeSet)):
                is_changeset = True
                embedded_changeset = True
                break
            if is_changeset:
                continue

            ## diff normal graphs
            orig = self.handler.get(graph)
            if orig == None:
                orig = Graph(identifier=graph.identifier)
            changes = cs.diff(orig, graph)

        cs.commit()
        if embedded_changeset or cs:
            self.handler.put(self.store)

        return cs

    def rollback(self):
        """
        Roll back any pending changes in this context

        This simply emptying it of graphs that have been previously added using
        :meth:`add`.
        """
        dummy = Graph("IOMemory")
        self.store = dummy.store


class Handler(object):
    """
    Handle reading and writing of RDF Graphs

    Storage back-ends are registered to an instance of this class for reading and
    writing. It distributes read and write (:meth:get and :meth:put) operations over
    these back ends. 

    Both the write case and some more complex read operations are intimately tied 
    to the use of :class:`ordf.changeset.ChangeSet` to which this class is the
    main entry point - it would be unusual, for example, to create a *ChangeSet*
    directly.

    .. code-block:: python

        ## initialise some storage
        null_storage = HandlerPlugin()

        ## create the handler
        handler = Handler()

        ## register the storage
        handler.register_reader(null_storage)
        handler.register_writer(null_storage)

        ## a read operation: retrieve a graph from storage
        handler.get(graph_identifier)
 
        ## a write operation: saving with a change context
        ctx = handler.context("username", "change reason")
        ctx.add(some_graph)
        ctx.commit()

    If using the :func:init_handler function instead of constructing
    the handler by hand (which is recommended) then for each storage
    module will have a "handler" attribute set by that function that
    refers back to the handler.

    Likewise, the handler will have the name of the storage module
    set as an attribute. e.g.::

    .. code-block:: python

        getattr(handler, "xapian")

    will return the instance of the xapian storage module.

    .. automethod:: register_reader
    .. automethod:: register_writer
    .. automethod:: get
    .. automethod:: put
    .. automethod:: remove
    .. automethod:: context
    .. automethod:: changeset
    .. automethod:: history
    .. automethod:: construct
    .. automethod:: query

    """
    def __init__(self, **kw):
        self.__readers__ = []
        self.__writers__ = []
        self.__kw__ = kw
        self.log = logging.getLogger(__name__)
        ordf = pkg_resources.get_distribution("ordf")
        self.log.info("%s initialised ver %s" % (self, ordf.version))

    def __str__(self):
        return self.__class__.__name__ + "(%s/%s)" % (len(self.__readers__), len(self.__writers__))

    def connect(self, *av, **kw):
        """
        Intended for subclasses, anything that must be done to connect the 
        handler to e.g. a message queue should be done here
        """
    def close(self, *av, **kw):
        """
        Intended for subclasses, do any cleanup required to shut down
        """

    def register_reader(self, handler, *av, **kw):
        """
        Register a writer back-end.

        :param handler: either an instance of (a sub-class of) :class:HandlerPlugin or 
            a string. If a string, then uses :meth:HandlerPlugin.find to locate the
            appropriate implementation.

        :param av: positional arguments passed to the handler's constructor when
            *handler* is named with a string.

        :param kw: ditto keyword arguments.
        """
        if isinstance(handler, basestring):
            handler_cls = HandlerPlugin.find(handler)
            handler = handler_cls(*av, **kw)
        self.__readers__.append(handler)
        self.log.info("%s reading from %s" % (self, handler))

    def register_writer(self, handler, *av, **kw):
        """
        Register a writer back-end.

        Parameters are as for :meth:register_reader
        """
        if isinstance(handler, basestring):
            handler_cls = HandlerPlugin.find(handler)
            handler = handler_cls(*av, **kw)
        self.__writers__.append(handler)
        self.log.info("%s writing to %s" % (self, handler))

    def put(self, *av, **kw):
        """
        Iterates over all of the registered write handlers and calls
        their *put* method.

        The *put* methods are called with the given positional and keyword
        arguments.
        """
        for h in self.__writers__:
            if h.put(*av, **kw):
                return

    def get(self, *av, **kw):
        """
        Iterates over all of the registered write handlers and
        calls their *get* method.

        The first back-end to return a non-*None* value wins and this value
        is returned.

        The *get* methods are called wwith the given positional and keyword
        arguments.
        """
        for h in self.__readers__:
            result = h.get(*av, **kw)
            if result is not None:
                result.handler = self
                return result

    def append(self, *av, **kw):
        """
        Append to the given graph
        """
        for h in self.__writers__:
            h.append(*av, **kw)
            
    def remove(self, *av, **kw):
        """
        Remove the graph from all storage and indices
        """
        for h in self.__readers__:
            h.remove(*av, **kw)

    def context(self, user, reason):
        """
        Return an instance of :class:ChangeContext bound to this
        handler

        :param user: The user (presumed already authenticated via whatever 
            mechanism) requesting the change

        :param reason: A short description of the nature of the changes being
           made.
        """
        return ChangeContext(self, user, reason, **self.__kw__)

    def changeset(self, csid, *av, **kw):
        """
        Given a *ChangeSet* identifier, return a changeset
        """
        g = self.get(csid, *av, **kw)
        return ChangeSet(store=g.store, identifier=g.identifier)

    def history(self, identifier):
        """
        return the history of the graph
        
        :param identifier: a *Graph* or identifier
            
        :return: generator of changesets for the given graph, most
           recent first. Values yielded by the generator will be either
           instances of :class:ordf.changeset.ChangeSet or lists in the
           case of multiple parents. This latter is not well tested.
        """
        graph = self.get(identifier)

        def walk_history(csid):
            cs = self.changeset(csid)
            yield cs
            parents = []
            for s,p,csid in cs.triples((csid, CS.precedingChangeSet, None)):
                parents.append(csid)
            if len(parents) == 1:
                for cs in walk_history(parents[0]):
                    yield cs
            if len(parents) > 1:
                yield [walk_history(csid) for csid in parents]

        csid = graph.version()
        if csid is not None:
            for cs in walk_history(csid):
                yield cs

    def construct(self, identifier):
        """
        Construct the requested graph from stored changesets

        :param identifier: a *Graph* or identifier
        """
        history = list(self.history(identifier))
        history.reverse()

        g = Graph(identifier=identifier)
        for cs in history:
            cs.apply(g)
        return g

    def query(self, q):
        """
        Execute a SPARQL query if we have a back-end that supports
        such.

        :param q: the query
        """
        if hasattr(self, "fourstore"):
            return self.fourstore.query(q, initNs=namespaces)
        elif hasattr(self, "rdflib"):
            prefixes = ["PREFIX %s: <%s>" % (k, namespaces[k]) for k in namespaces]
            q = "\n".join(prefixes) + "\n" + q
            return self.rdflib.query(q)
        else:
            raise AttributeError("No SPARQL Implementations")

class HandlerPlugin(object):
    """
    Instances of this class implement read and/or write operations on storage
    and indices.

    This is an interface specification for subclassing and null implementation.

    The :meth:find class method is used to create handler implementations that may
    live in various modules. To do this it makes use of the *pkg_resources.EntryPoint*
    mechanism. For example, looking at ORDF's *setup.py* you can find the entrypoints
    for the handler implementations that are bundled with this software::
    
        [ordf.handler]
        pairtree=ordf.handler.pt:PairTree
        rdflib=ordf.handler.rdf:RDFLib
        fourstore=ordf.handler.rdf:FourStore
        xapian=ordf.handler.xap:Xapian
        rabbit=ordf.handler.queue:Rabbit

    .. automethod:: connect
    .. automethod:: find
    .. automethod:: get
    .. automethod:: put
    """
    @classmethod
    def find(cls, name):
        """
        Search in the *pkg_resources.EntryPoint* named *[ordf.handler]*
        for a concrete subclass implementing this interface.
            
        :param name: the name of the plugin to find

        If a result is found but is not a subclass of :class:`HandlerPlugin` a
        *ValueError* is raised. If no result is found, an *ImportError* is
        raised.
        """
        for entrypoint in pkg_resources.iter_entry_points(group="ordf.handler"):
            if entrypoint.name == name:
                plugin = entrypoint.load()
                if not issubclass(plugin, cls):
                    raise ValueError("%s is not a subclass of %s" % (plugin, cls))
                return plugin
        raise ImportError("no plugin in [ordf.handler] named %s" % name)

    def connect(self, *av, **kw):
        """
        """

    def put(self, graph):
        """
        Save or index the given conjunctive graph
        """
        if isinstance(graph, _Graph):
            contexts = [graph]
        else:
            contexts = graph.contexts()
        for ctx in contexts:
            self[ctx] = ctx

    def get(self, identifier):
        """
        Retrieve the requested graph

        :param identifier: may be a string or :class:rdflib.term.URIRef or an instance
            of :class:`rdflib.graph.Graph` in which latter case the graph's *identifier*
            is used as  lookup key.
        """
        return self[identifier]

    def append(self, frag):
        """
        Append the fragment to the given graph
        """
        graph = self.handler.get(frag.identifier)
        if graph is not None:
            graph += frag
        else:
            graph = frag
        self.put(graph)
                                                
    def remove(self, identifier):
        """
        Remove the requested graph. Arguments as for :meth:get
        """
        del self[identifier]

    def __getitem__(self, key):
        """
        Implement in concrete subclasses
        """
    def __setitem__(self, key, value):
        """
        Implement in concrete subclasses
        """
    def __delitem__(self, key):
        """
        Implement in concrete subclasses
        """

class ConfigError(Exception):
    """
    Raised on configuration error
    """

def get_args(config, name):
    av = config.get(name + ".args")
    if av:
        av = [av]
    else:
        av = []
    kw = {}
    pfxlen = len(name) + 1
    for k in config.keys():
        if k.startswith(name + ".") and k != name + ".args" and not name.startswith(name + ".connect."):
            kw[k[pfxlen:]] = config[k]
    return av, kw

def init_handler(config):
    """
    Initialise a handler based on the configuration dictionary. Typically
    *config* will be a section of a configuration file parsed with
    :class:`ConfigParser` either directly or accessed via :data:`pylons.config`

    The type of handler to be created, the reading and writing plugins and
    their initialisation arguments can all be specified::

        [app:main]

        ## handler class to use
        ordf.handler = ordf.handler.Handler

        ## if a handler has a connect() method, it is run with arguments 
        ## following. this is used e.g. for ordf.handler.queue.RabbitHandler
        ordf.connect.queue = readerqueue

        ## reader plugins
        ordf.readers = pairtree

        ## writer plugins
        ordf.writers = pairtree,fourstore,xapian,rabbit

        ## arguments for the back-ends
        pairtree.args = /some/where/data/pairtree
        fourstore.args = kbname,soft_limit=-1
        xapian.args = 127.0.0.1:44332
        rabbit.connect.exchange = foo

    Each storage module added to the handler (as a readoer or as a writer)
    will have a "handler" attribute set by this function that refers back
    to the handler. In this way storage/index modules that require access
    to the handler (currently only :class:`~ordf.handler.fuxi.FuXiReasoner`)
    have it.

    Likewise, the handler will have the name of the storage module
    set as an attribute. e.g.::

    .. code-block:: python

        getattr(handler, "xapian")

    will return the instance of the xapian storage module. In this way 
    application code can treat the *handler* instance as a singleton and
    access the various back-ends simply. It is then possible to call 
    specialised search or other methods as needed.
    """

    av, kw = get_args(config, "ordf.handler")
    if "ordf.handler" in config:
        modname, clsname = config["ordf.handler"].split(":")
        mod = __import__(modname, globals(), locals(), [clsname])
        cls = getattr(mod, clsname)
    else:
        cls = Handler
    handler = cls(*av, **kw)

    av, kw = get_args(config, "ordf.connect")
    handler.connect(*av, **kw)

    ## special
    readers = config.get("ordf.readers", None)
    if readers is not None:
        for reader in readers.split(","):
            if not reader: continue
            if hasattr(handler, reader):
                storage = getattr(handler, reader)
            else:
                av, kw = get_args(config, reader)
                storage_cls = HandlerPlugin.find(reader)
                storage = storage_cls(*av, **kw)
                setattr(handler, reader, storage)
                setattr(storage, "handler", handler)
                av, kw = get_args(config, reader + ".connect")
                storage.connect(*av, **kw)
            handler.register_reader(storage)

    writers = config.get("ordf.writers", None)
    if writers is not None:
        for writer in writers.split(","):
            if not writer: continue
            if hasattr(handler, writer):
                storage = getattr(handler, writer)
            else:
                av, kw = get_args(config, writer)
                storage_cls = HandlerPlugin.find(writer)
                storage = storage_cls(*av, **kw)
                setattr(handler, writer, storage)
                setattr(storage, "handler", handler)
                av, kw = get_args(config, writer + ".connect")
                storage.connect(*av, **kw)
            handler.register_writer(storage)

    return handler
