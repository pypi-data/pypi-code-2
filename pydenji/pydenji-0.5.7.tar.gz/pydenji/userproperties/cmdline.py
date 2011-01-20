#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.
#
# Commandline integration for property mapping.


class CommandLinePropertyParser(object):
    def parse(self, arglist):
        return [ arg[3:] for arg in arglist if arg.startswith("-PD") ]


