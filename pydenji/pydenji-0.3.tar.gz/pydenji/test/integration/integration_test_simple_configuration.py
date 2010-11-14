#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

# very rough and basic integration test. To be extended.

import os
from unittest import TestCase
from pkg_resources import resource_filename as rfn

from pydenji.test.integration.simple_app import *

from pydenji.appcontext.context import AppContext
from pydenji.userproperties.mapping import inject_properties_from
from pydenji.userproperties.overrider import override_with
from pydenji.config.pythonconfig import Configuration, prototype, singleton


@override_with(rfn("pydenji", "test/integration/resources/propertyconf.properties"))
@Configuration
class MyRemoteFetchService(object):
    target_address = "somenetworkaddress"

    def network_service(self):
        return SomeService(self.networked_factory)

    @prototype
    def networked_factory(self):
        return SomeNetworkedClass(self.connector(), self.resource())

    @prototype
    def connector(self):
        return SomeConnector(self.target_address)


    @singleton.lazy
    def resource(self):
        return SomeResource

class TestSimpleConfiguration(TestCase):
    def setUp(self):
        try:
            os.unlink("/tmp/pydenji_simple_configuration_test_somenetworkaddress")
        except:
            pass

    def test_basic(self):
        context = AppContext(MyRemoteFetchService())
        network_service = context.get_object("network_service")
        network_service.performAction()
        self.assertTrue(os.path.exists("/tmp/pydenji_simple_configuration_test_somenetworkaddress"), "missing file it should be created")
        os.unlink("/tmp/pydenji_simple_configuration_test_somenetworkaddress")


