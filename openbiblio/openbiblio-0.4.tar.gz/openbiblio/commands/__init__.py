from paste.script.command import Command as PasteCommand, BadCommand
from openbiblio.config.environment import load_environment
from paste.deploy import appconfig
from glob import glob
from getpass import getuser
from ordf.graph import Graph
from ordf.term import URIRef, Literal
from ordf.namespace import Namespace

import os

log = __import__("logging").getLogger(__name__)
class Command(PasteCommand):
    group_name = "openbiblio"
    def parse_args(self, *av, **kw):
        super(Command, self).parse_args(*av, **kw)
        if not self.args:
            raise BadCommand("please specify a configuration file")
        config = self.args[0]
        self.args = self.args[1:]
        self.parse_config(config)

    def parse_config(self, config_file):
        ### parse the config file
        if not config_file.startswith("/"):
            context = { "relative_to": os.getcwd() }
        else:
            context = {}
        self.logging_file_config(config_file)
        self.config = appconfig('config:' + config_file, **context)
        import pylons
        pylons.config = self.config
        load_environment(self.config.global_conf, self.config.local_conf)

class Fixtures(Command):
    summary = "Load Fixtures"
    usage = "config.ini"
    parser = Command.standard_parser(verbose=False)
    done = False
    obproot = os.path.dirname(os.path.dirname(__file__))
    testdata = os.path.join(obproot, "tests", "data")

    @classmethod
    def data(cls):
        ident = URIRef("http://bibliographica.org/test")
        data = Graph(identifier=ident)
        data.parse(os.path.join(cls.testdata, "fixtures.rdf"))
        yield data

    @classmethod
    def setUp(cls):
        from openbiblio import handler

        if cls.done:
            return

        ctx = handler.context(getuser(), "Initial Data")
        for graph in cls.data():
            ## delete any stale history
            ctx.add(graph)
        ctx.commit()

        ctx = handler.context(getuser(), "Bibtex Graph data")
        for item in ['GB9361575', 'GB5000065','GB5006595']:
            ident = URIRef("http://bnb.bibliographica.org/entry/%s" % item)
            data = Graph(identifier=ident)
            data.parse(os.path.join(cls.testdata, "%s.rdf" % item))
            ctx.add(data)
        ctx.commit()
        
        cls.done = True

    @classmethod
    def tearDown(cls):
        pass

    def command(self):
        self.setUp()

class CleanDB(Command):
    summary = "Empties database"
    usage = "config.ini"
    parser = Command.standard_parser(verbose=False)
    done = False
    obproot = os.path.dirname(os.path.dirname(__file__))
    testdata = os.path.join(obproot, "tests", "data")

    @classmethod
    def cleanup(cls):
        from openbiblio import handler
        from ordf.graph import Graph, ConjunctiveGraph
        store = handler.__writers__[0].store
        cg = ConjunctiveGraph(store)
        for graph in cg.contexts():
            toremove = (graph.identifier.startswith('http://bibliographica.org')
                or # changesets
                graph.identifier.startswith('urn:uuid')
                or
                graph.identifier.startswith('http://bnb.bibliographica.org')
                )
            if toremove:
                store.remove((None, None, None), graph)
        store.commit()

        # virtuoso specific ...
        store.cursor().execute('RDF_GLOBAL_RESET ()')


    def command(self):
        self.cleanup()

class UpdateUsers(Command):
    summary = "Adds gravatar information and api keys to already existing users."
    usage = "config.ini"
    parser = Command.standard_parser(verbose=False)
    done = False
    obproot = os.path.dirname(os.path.dirname(__file__))

    @classmethod
    def update(cls):
        from openbiblio import handler, model
        from uuid import uuid4

        for user in model.Account.find():
            try:
                user.apikey
            except AttributeError:
                user.apikey = Literal(uuid4())
            if len(list(user.avatar)) == 0:
                user.avatar = user.get_avatar
            user.save("system", 'updated user: %s' %  user.identifier.n3())

    def command(self):
        self.update()

