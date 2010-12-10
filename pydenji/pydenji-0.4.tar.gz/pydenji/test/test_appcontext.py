#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni

from unittest import TestCase

from pydenji.appcontext import AppContext, is_appcontext_aware
from pydenji.config.contextconfig import ContextConfiguration
from pydenji.config.pythonconfig import singleton, dontconfigure
from pydenji.config.pythonconfig import Configuration

class TestAppContext(TestCase):
    def test_appcontext_allows_retrieving_by_name(self):
        @Configuration
        class MockConf(object):
            @singleton
            def something(self):
                return 1

        context = AppContext(MockConf())
        something = context.get_object("something")
        self.assertEquals(1, something)

    def test_appcontext_supports_multiple_configs(self):
        # TODO: this functionality might be overlapping to CompositeConfig.
        # think about it.
        
        @Configuration
        class MockConf(object):
            @singleton
            def something(self):
                return 1

        @Configuration
        class OtherConf(object):
            @singleton
            def otherthing(self):
                return 2

        context = AppContext(MockConf(), OtherConf())
        something = context.get_object("something")
        self.assertEquals(1, something)
        otherthing = context.get_object("otherthing")
        self.assertEquals(2, otherthing)



    def test_appcontext_fetches_objects_eagerly_when_required(self):
        c = set()
        @Configuration
        class MockConf(object):
            @singleton
            def something(self):
                c.add("something")

            @singleton
            def _private(self):
                c.add("private")
             

        conf = MockConf()
        context = AppContext(conf)
        self.assertEquals(set(["something", "private"]), c)

        
    def test_appcontext_fetches_objects_lazily_when_required(self):
        c = []
        @Configuration
        class MockConf(object):
            @singleton.lazy
            def something(self):
                c.append(True)


        conf = MockConf()
        context = AppContext(conf)
        self.assertEquals([], c)

    def test_appcontext_gets_injected_on_aware_objects(self):
        # TODO: think whether we need to use an ABC instead or as well.
        class AppAwareObject(object):
            app_context = None
            
            def set_app_context(self, context):
                self.app_context = context

        @Configuration
        class MockConf(object):
            @singleton
            def appcontextaware(self):
                return AppAwareObject()


        context = AppContext(MockConf())
        aware = context.get_object("appcontextaware")
        self.assertTrue(context is aware.app_context, "context wasn't injected correctly!")

    def test_appcontext_gets_injected_on_aware_configuration_objects(self):
        @Configuration
        class MockConf(object):
            @dontconfigure
            def set_app_context(self, context):
                self.app_context = context

        conf = MockConf()
        context = AppContext(conf)
        self.assertTrue(context is conf.app_context, "context wasn't injected correctly!")


class TestGlobalConfig(TestCase):
    def test_global_config_falls_back_on_appcontext_factories(self):
        
        class One(object):
            def relies_on_other(self):
                return self.other() * 2
            
        class Other(object):
            def other(self):
                return 2

        one = ContextConfiguration(One)()
        other = Configuration(Other)()

        context = AppContext(one, other)
        self.assertEquals(4, context.get_object("relies_on_other"))


    



