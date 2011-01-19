#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

# very rough and basic integration test. To be extended.

import os
from unittest import TestCase

from pydenji.test.integration.simple_app import *

from pydenji.appcontext.context import AppContext
from pydenji.userproperties.mapping import inject_properties_from
from pydenji.userproperties.overrider import override_with
from pydenji.config.pythonconfig import Configuration, prototype, singleton
from pydenji.uriresolver import resource_filename_resolver as rfr
from pydenji.placeholders import Placeholder


@inject_properties_from(rfr("pkg://pydenji/test/integration/resources/inject.conf"))
@override_with(rfr("pkg://pydenji/test/integration/resources/propertyconf.properties"))
@Configuration
class MyRemoteFetchService(object):
    target_address = Placeholder("target_address")

    def __init__(self, props):
        self.target_address = props["target_address"]

    #automagic singleton
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
        return SomeResource()

class TestSimpleConfiguration(TestCase):
    def setUp(self):
        try:
            os.unlink("/tmp/pydenji_simple_configuration_test_somenetworkaddress")
        except:
            pass

    def test_network_service_fetching(self):
        context = AppContext(MyRemoteFetchService())
        network_service = context.get_object("network_service")
        network_service.performAction()
        # the file should be created by connector instance, whose prefix was overriden.
        self.assertTrue(os.path.exists("/tmp/pydenji_simple_configuration_test_somenetworkaddress"), "missing file it should be created")
        os.unlink("/tmp/pydenji_simple_configuration_test_somenetworkaddress")
