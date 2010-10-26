#!/usr/bin/python
"""
Introduction
============
  Test suite for Schema module from the gerald framework

  Note that this suite uses the py.test module 
  (http://codespeak.net/py/current/doc/test.html)

Approach
========
  Test only those things that are specific to the Schema module

"""
__date__ = (2009, 12, 21)
__version__ = (0, 4, 1)
__author__ = "Andy Todd <andy47@halfcooked.com>"

import os

from gerald import Schema
from gerald.utilities.Log import get_log

import py.test

LOG_FILENAME = os.path.join(os.environ['HOME'], 'Temp', 'test_schema.log')
log = get_log('test_schema', LOG_FILENAME, 'INFO')

class TestNotImplemented(object):
    "Unit tests for methods not implemented in Schema"
    def test_get_schema(self):
        "Make sure that the Schema._get_schema method isn't implemented"
        new_schema = Schema.Schema('empty')
        py.test.raises(NotImplementedError, new_schema._get_schema, None)

    def test_get_table(self):
        "Make sure that the Table._get_table method isn't implemented"
        new_table = Schema.Table('empty')
        py.test.raises(NotImplementedError, new_table._get_table, None)

    def test_get_table_ddl(self):
        "Make sure that the Table.get_ddl method isn't implemented"
        new_table = Schema.Table('empty')
        py.test.raises(NotImplementedError, new_table.get_ddl)

    def test_get_view(self):
        "Make sure that the View._get_view method isn't implemented"
        new_view = Schema.View('empty')
        py.test.raises(NotImplementedError, new_view._get_view, None)

    def test_get_view_ddl(self):
        "Make sure that the View.get_ddl method isn't implemented"
        new_view = Schema.View('empty')
        py.test.raises(NotImplementedError, new_view.get_ddl)

    def test_get_trigger(self):
        "Make sure that the Trigger._get_trigger method isn't implemented"
        new_trigger = Schema.Trigger('empty')
        py.test.raises(NotImplementedError, new_trigger._get_trigger, None)

    def test_get_trigger_ddl(self):
        "Make sure that the Trigger.get_ddl method isn't implemented"
        new_trigger = Schema.Trigger('empty')
        py.test.raises(NotImplementedError, new_trigger.get_ddl)

    def test_get_sequence(self):
        "Make sure that the Sequence._get_sequence method isn't implemented"
        new_sequence = Schema.Sequence('empty')
        py.test.raises(NotImplementedError, new_sequence._get_sequence, None)

    def test_get_sequence_ddl(self):
        "Make sure that the Sequence.get_ddl method isn't implemented"
        new_sequence = Schema.Sequence('empty')
        py.test.raises(NotImplementedError, new_sequence.get_ddl)

    def test_get_code_object(self):
        "Make sure that the CodeObject._get_code_object method isn't implemented"
        new_code_object = Schema.CodeObject('empty', 'dummy')
        py.test.raises(NotImplementedError, new_code_object._get_code_object, None)

    def test_get_code_object_ddl(self):
        "Make sure that the CodeObject.get_ddl method isn't implemented"
        new_code_object = Schema.CodeObject('empty', 'dummy')
        py.test.raises(NotImplementedError, new_code_object.get_ddl)

