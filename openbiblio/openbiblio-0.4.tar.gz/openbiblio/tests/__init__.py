"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

from openbiblio.commands import Fixtures

__all__ = ['environ', 'url', 'test_graph', 'TestController', 'delete_all']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([pylons.test.pylonsapp.config['__file__']])

test_graph = "http://bnb.bibliographica.org/entry/GB5006595"

environ = {}

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        wsgiapp = pylons.test.pylonsapp
        config = wsgiapp.config
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    def setUp(self):
        Fixtures.setUp()

    def tearDown(self):
        Fixtures.tearDown()

def delete_all():
    '''Remove all openbiblio related graphs from the store.
    
    '''
    # TODO: not working properly and not all graphs deleted - not sure why
    # TODO: none of changeset graphs get picked up here (not sure why)
    from openbiblio import handler
    from ordf.graph import Graph, ConjunctiveGraph
    for graph, in handler.query("SELECT DISTINCT ?g WHERE { GRAPH ?g { ?s ?p ?o } }"):
        toremove = (graph.startswith('http://bibliographica.org')
            or # changesets
            graph.startswith('urn:uuid')
            or
            graph.startswith('http://bnb.bibliographica.org')
            )
        if toremove:
            handler.remove(graph)

    # virtuoso specific ...
    #store.cursor().execute('RDF_GLOBAL_RESET ()')

