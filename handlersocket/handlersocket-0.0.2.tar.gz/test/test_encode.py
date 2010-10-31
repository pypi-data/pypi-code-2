#!/usr/bin/env python
# coding: utf-8

from nose.tools import *
import handlersocket.client as client

def test_escape():
    s = 'a\x00b\x01c\x0fd\x10e'
    e = client._escape(s)
    assert_equal(e, 'a\x01\x40b\x01\x41c\x01\x4fd\x10e')
    u = client._unescape(e)
    assert_equal(u, s)

