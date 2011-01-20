#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

from unittest import TestCase

from pydenji.userproperties.cmdline import CommandLinePropertyParser

class TestCmdlineIntegration(TestCase):
    def test_cmdline_arguments_starting_with_PD_are_parsed(self):
        parser =  CommandLinePropertyParser()
        # we'd like to feed those to configparser?
        self.assertEquals(["somevalue=1"], parser.parse(["-PDsomevalue=1" , "--someother"]))