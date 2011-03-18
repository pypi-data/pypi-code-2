"""
Test Pairtree storage of models
"""
import os
import tempfile
import shutil

from ordf.tests import our_test_graph, identifier
from ordf.handler import Handler
from ordf.handler.pt import PairTree


class TestPairtreeStorage:
    @classmethod
    def setup_class(self):
        self.tmpdir = os.path.join(tempfile.gettempdir(), self.__name__)
        self.ptree = PairTree(self.tmpdir)

    @classmethod
    def teardown_class(self):
        shutil.rmtree(self.tmpdir)

    def test_01_create(self):
        self.ptree[identifier] = our_test_graph()

    def test_02_read(self):
        fsobj = self.ptree[identifier]

    def test_03_delete(self):
        del self.ptree[identifier]

    def test_04_graphops(self):
        self.ptree.put(graph=our_test_graph())
        self.ptree.get(our_test_graph())
        self.ptree.remove(our_test_graph())

    def test_05_handler(self):
        handler = Handler()
        handler.register_reader(self.ptree)
        handler.register_writer(self.ptree)
        ctx = handler.context("ptree_test", "ptree_test")
        ctx.add(our_test_graph())
        ctx.commit()

        for cs in handler.history(identifier):
            self.ptree.remove(cs)
        self.ptree.remove(our_test_graph())

