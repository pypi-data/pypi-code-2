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
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp
from ordf.handler import init_handler
from ordf.graph import Graph
from ordf.term import URIRef
from getpass import getuser
import os

import pylons.test

__all__ = ['environ', 'url', 'TestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])

environ = {}

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)

    handler = init_handler(config)
    test_graph = URIRef("http://localhost:5000/test")

    def setUp(self):
        tests = os.path.dirname(__file__)
        testdata = os.path.join(tests, "data")
        data = Graph(identifier=self.test_graph)
        data.parse(os.path.join(testdata, "fixtures.n3"), format="n3")
        ctx = self.handler.context(getuser(), "fixture set up")
        ctx.add(data)
        ctx.commit()

    def tearDown(self):
        data = Graph(identifier=self.test_graph)
        ctx = self.handler.context(getuser(), "fixture tear down")
        ctx.add(data)
        ctx.commit()
