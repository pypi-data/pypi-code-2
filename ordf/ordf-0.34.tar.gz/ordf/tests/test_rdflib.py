"""
Test rdflib storage of models
"""
import tempfile
import shutil

from ordf.tests import our_test_graph, identifier
from ordf.handler import Handler
from ordf.handler.rdf import RDFLib


class TestRdflibStorage:
    @classmethod
    def setup_class(self):
        self.tmpdir = tempfile.mkdtemp()
        self.rdf = RDFLib(self.tmpdir, store="Sleepycat")

    @classmethod
    def teardown_class(self):
        shutil.rmtree(self.tmpdir)

    def test_01_create(self):
        self.rdf[identifier] = our_test_graph()

    def test_02_read(self):
        g = self.rdf[identifier]

    def test_03_delete(self):
        del self.rdf[identifier]

    def test_04_graphops(self):
        self.rdf.put(graph=our_test_graph())
        self.rdf.get(our_test_graph())
        self.rdf.remove(our_test_graph())

    def test_05_handler(self):
        handler = Handler()
        handler.register_reader(self.rdf)
        handler.register_writer(self.rdf)
        ctx = handler.context("rdflib_test", "rdflib_test")
        ctx.add(our_test_graph())
        ctx.commit()

        for cs in handler.history(identifier):
            self.rdf.remove(cs)
        self.rdf.remove(our_test_graph())

