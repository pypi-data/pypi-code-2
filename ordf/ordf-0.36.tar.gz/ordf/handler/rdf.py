"""
This module implements some triplestores. Most basic but least 
scalable is the storage that comes with `RDFLib`_. More advanced
and scalable but more complicated to set up is `4store`_.

RDFLib Basic Storage -- :class:`RDFLib`
---------------------------------------
.. autoclass:: RDFLib
   :show-inheritance:

4Store Quad-Store -- :class:`FourStore`
---------------------------------------
.. autoclass:: FourStore
   :show-inheritance:

.. _RDFLib: http://www.rdflib.net/
.. _4store: http://4store.org/
"""

__all__ = ["RDFLib", "FourStore"]

from rdflib import plugin
from rdflib.store import Store
from ordf.graph import Graph, _Graph, ConjunctiveGraph
from ordf.utils import get_identifier
from ordf.handler import HandlerPlugin
from logging import getLogger

class RDFLib(HandlerPlugin):
    """
    The RDFLib handler can use any of the back-ends that are supported
    by rdflib itself. The constructor takes a *store* keyword argument
    that specifies which to use. This defaults to *"IOMemory"* which is
    not terribly useful. Initialisation arguments for the store should
    be passed as positional arguments, for example::

        RDFLib("/some/where/data", store="Sleepycat")

    or the equivalent in the configuration file,::

        rdflib.args = /some/where/data
        rdflib.store = Sleepycat
    """
    def __init__(self, *av, **kw):
        kw = kw.copy()
        store = kw.setdefault("store", "IOMemory")
        del kw["store"]
        self.log = getLogger(__name__ + "." + self.__class__.__name__)
        if isinstance(store, basestring):
            store_cls = plugin.get(store, Store)
            self.log.info("Initialising %s storage" % store_cls.__name__)
            store = store_cls(*av, **kw)
        self.store = store
    def __getitem__(self, k):
        ## Careful, the graph in the store is to be treated 
        ## as read-only unless a set operation is made.
        ## Unfortunately this means we have to copy it
        ident = get_identifier(k)
        orig = Graph(self.store, identifier=ident)
        new = Graph(identifier=ident)
        new += orig
        return new
    def __setitem__(self, k, g):
        assert isinstance(g, _Graph)
        old = Graph(self.store, identifier=get_identifier(k))
        old.remove((None, None, None))
        for statement in g.triples((None, None, None)):
            old.add(statement)
        if hasattr(self.store, "sync"):
            self.store.sync()
    def __delitem__(self, k):
        old = Graph(self.store, identifier=get_identifier(k))
        old.remove((None, None, None))
        if hasattr(self.store, "sync"):
            self.store.sync()

    def append(self, g):
        old = Graph(self.store, identifier=g.identifier)
        old += g
        if hasattr(self.store, "sync"):
            self.store.sync()
                                    
    def remove(self, g):
        del self[g]

    def query(self, *av, **kw):
        if hasattr(self.store, "query"):
            return self.store.query(*av, **kw)
        else:
            g = ConjunctiveGraph(self.store)
            return g.query(*av, **kw)

    def commit(self):
        self.store.commit()
    def rollback(self):
        self.store.rollback()
        
class FourStore(RDFLib):
    """
    Use of this back-end requires the `py4s`_ bindings to `4store`_.
    It also requires 4store to be built from the `multiclient branch`_
    to support multiple simultaneous client connections.

    Initialisation takes a comma-separated string of arguments,
    only the first, the name of the *kb* is required. For example::

        FourStore("kbname")
        FourStore("kbname,soft_limit=-1")

    or equivalently in the configuration file::

        fourstore.args = kbname
        fourstore.args = kbname,soft_limit=-1

    .. _py4s: http://github.com/wwaites/py4s
    .. _multiclient branch: http://github.com/wwaites/4store
    """
    def __init__(self, config):
        from py4s import LazyFourStore
        self.store = LazyFourStore(config)
    def __setitem__(self, k, g):
        assert isinstance(g, _Graph)
        ident = get_identifier(k)
        cursor = self.store.cursor()
        cursor.add_graph(g, replace=True)
    def __delitem__(self, k):
        ident = get_identifier(k)
        cursor = self.store.cursor()
        cursor.delete_graph(ident)
    def append(self, frag):
        ident = get_identifier(frag)
        cursor = self.store.cursor()
        cursor.add_graph(frag, replace=False)
    def query(self, *av, **kw):
        return self.store.query(*av, **kw)
