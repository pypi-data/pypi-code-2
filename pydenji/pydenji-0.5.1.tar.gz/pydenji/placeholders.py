#!/usr/bin/env python
# -*- coding: utf-8 -*-
# (C) 2010 Alan Franzoni.

# TODO: add unit tests for this.

class UnconfiguredError(Exception):
    def __init__(self, name):
        Exception.__init__(self, "'%s' placeholder has not been configured!" % name)

class Placeholder(object):
    def __init__(self, name):
        object.__setattr__(self, "name", name)

    def __getattr__(self, attr):
        raise UnconfiguredError, self.name

    def __setattr__(self, attr, value):
        raise UnconfiguredError, self.name


PH = Placeholder # quick alias
