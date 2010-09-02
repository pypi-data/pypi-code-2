#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from unittest import TestCase

from pydenji.config.composite import CompositeConfig, NamingClashException
from pydenji.config.pythonconfig import prototype, singleton

class FirstConfig(object):
    @singleton
    def first(self):
        return 1

class SecondConfig(object):
    @prototype
    def second(self):
        return 2

class SecondBisConfig(object):
    @singleton
    def second(self):
        return 3

    @prototype
    def _private(self):
        return 1

class TestCompositeConfig(TestCase):

    def test_composite_config_merges_input_configs(self):
        first = FirstConfig()
        second = SecondConfig()
        
        composite = CompositeConfig((first, second))

        self.assertEquals(1, composite.first())
        self.assertEquals(2, composite.second())

    def test_composite_config_raises_error_if_name_clash_occurs(self):
        first = SecondConfig()
        second = SecondBisConfig()

        self.assertRaises(NamingClashException, CompositeConfig, (first, second))

    def test_composite_config_doesnt_expose_private_factories(self):
        first = FirstConfig()
        second = SecondBisConfig()

        composite = CompositeConfig((first, second))

        self.assertRaises(AttributeError, getattr, composite, "_private")


