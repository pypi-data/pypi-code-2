import os
import tempfile
import shutil

from ordf.handler import Handler, HandlerPlugin
from ordf.namespace import RDF, Namespace
from ordf.graph import Graph
from ordf.tests import our_test_graph, identifier

class TestHandler:
    @classmethod
    def setup_class(self):
        self.tmpdir = os.path.join(tempfile.gettempdir(), self.__name__)
        ptree_cls = HandlerPlugin.find("pairtree")
        ptree = ptree_cls(self.tmpdir)
        self.handler = Handler(namespace=Namespace("http://example.org/changesets/"))
        self.handler.register_reader(ptree)
        self.handler.register_writer(ptree)

    @classmethod
    def teardown_class(self):
        shutil.rmtree(self.tmpdir)

    def test_01_find(self):
        assert HandlerPlugin.find("null") is not None

    def test_02_register(self):
        h = Handler()

        # test  direct registering of an instance
        r = HandlerPlugin()
        h.register_reader(r)

        # test registering by named plugin
        h.register_writer("null")


    def test_03_context(self):
        ctx = self.handler.context("test_handler", "create some data")
        ctx.add(our_test_graph())
        ctx.commit()

        g = our_test_graph()
        g.remove((None, RDF.type, None))
        ctx = self.handler.context("test_handler", "delete some data")
        ctx.add(g)
        ctx.commit()

    def test_04_undo(self):
        ## undo the last change (remove the types again)
        constructed = self.handler.get(identifier)
        ver = constructed.version()
        cs = self.handler.changeset(ver)
        cs.undo(constructed)

        ctx = self.handler.context("test_handler", "put data back")
        ctx.add(our_test_graph())
        ctx.commit()

    def test_05_construct(self):
        ## construct head from changes in previous step
        constructed = self.handler.construct(identifier)
        assert len(constructed) == len(our_test_graph()) + 1

