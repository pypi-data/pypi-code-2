"""
This is the core read/write storage module in ORDF. Its purpose is
to store RDF graphs in the filesystem in a specialised directory
hierarchy known as a Pairtree_. The reasoning behind this is explained
in the :ref:`rdf-back-end-design` section of this documentation.

.. autoclass:: PairTree
   :show-inheritance:

.. _Pairtree: https://confluence.ucop.edu/display/Curation/PairTree
"""

from pairtree import PairtreeStorageFactory, PartNotFoundException
from pairtree.pairtree_path import id_to_dirpath
from ordf.graph import Graph, _Graph
from ordf.term import URIRef
from ordf.utils import uuid, get_identifier
from ordf.handler import HandlerPlugin
from traceback import format_exc
from logging import getLogger

log = getLogger(__name__)

class PairTree(HandlerPlugin):
    """
    When adding a *Graph* to this store the first thing that is done is its 
    *uri* is normalised to the *urn:uuid:* namespace. If its idenfifier is
    already in that namespace, nothing is changed. If it is not, it is 
    converted. The original identifier is stored in the filesystem for later
    retrieval so that when a read operation is performed, the result is a
    *Graph* with the correct *uri* identifier. This is done with the utility
    function :func:`ordf.utils.uuid`.
    """
    def __init__(self, store_dir, uri_base="urn:uuid:"):
        f = PairtreeStorageFactory()
        self.store = f.get_store(store_dir=store_dir, uri_base=uri_base)

    def __getitem__(self, key):
        k = uuid(key).lstrip(self.store.uri_base)
        fsobj = self.store.get_object(k)
        #fsobj_dir = id_to_dirpath(k, self.store.pairtree_root)
        #print namaste.get(fsobj_dir)
        try:
            identifier = fsobj.get_bytestream("identifier.txt")
        except PartNotFoundException:
            identifier = get_identifier(key)
        g = Graph(identifier=URIRef(identifier))
        try:
            g.parse(fsobj.get_bytestream("graph.rdf", streamable=True), format="xml")
        except PartNotFoundException:
            pass
        return g

    def __setitem__(self, key, g):
        assert isinstance(g, _Graph)
        k = uuid(key).lstrip(self.store.uri_base)
        fsobj = self.store.get_object(k)
        fsobj.add_bytestream("identifier.txt", g.identifier)
        fsobj.add_bytestream("graph.rdf", g.serialize(format="xml"))

    def __delitem__(self, key):
        k = uuid(key).lstrip(self.store.uri_base)
        self.store.delete_object(k)

    def __iter__(self):
        for uuid in self.store.list_ids():
            identifier = "urn:uuid:" + uuid
            try:
                graph = self[identifier]
                yield graph
            except GeneratorExit:
                return
            except KeyboardInterrupt:
                raise
            except: 
                log.error("error reading %s:\n%s" % (identifier, format_exc()))
