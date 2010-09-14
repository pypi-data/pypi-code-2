# Copyright (c) 2009 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
Tests for pesto/utils.py
"""

from __future__ import with_statement

from cStringIO import StringIO, OutputType as cStringIO_OutputType

from nose.tools import assert_equal, assert_true

from pesto.utils import ExpandableOutput, PutbackInput, DelimitedInput


def test_expandableio():

    with ExpandableOutput(10) as eio:
        eio.write('abc')
        eio.seek(0)
        assert_equal(eio.read(), 'abc')
        assert_true(isinstance(eio._io, cStringIO_OutputType))
        eio.write('defghij')
        assert_true(isinstance(eio._io, cStringIO_OutputType))
        eio.write('k')
        assert_true(isinstance(eio._io, file))
        eio.seek(0)
        assert_equal(eio.read(), 'abcdefghijk')

def test_putbackio_nested_putbacks():
    s = StringIO('one,two,three')
    s.seek(0)
    p = PutbackInput(s)
    a = s.read(3)
    b = s.read(3)
    p.putback(b)
    p.putback(a)
    assert_equal(p.read(), 'one,two,three')

def test_putbackio_read_from_putback_short():
    """
    Test read for a length smaller than the putback buffer
    """
    s = StringIO('one,two,three')
    s.seek(0)
    p = PutbackInput(s)
    a = p.read(4)
    b = p.read(4)
    p.putback(b)
    p.putback(a)
    assert_equal(p.read(7), "one,two")

def test_putbackio_read_from_putback_and_stream_long():
    """
    Test read for a length longer than the putback buffer
    """
    s = StringIO('one,two,three')
    s.seek(0)
    p = PutbackInput(s)
    a = p.read(2)
    b = p.read(2)
    p.putback(b)
    p.putback(a)
    assert_equal(p.read(7), "one,two")

def test_putbackio_readline_from_putback_and_stream_short():
    """
    Test readline for a length shorter than the putback buffer
    """
    s = StringIO('one two\nthree four\n')
    s.seek(0)
    p = PutbackInput(s)
    a = p.read(4)
    b = p.read(4)
    p.putback(b)
    p.putback(a)
    assert_equal(p.readline(10), "one two\n")

def test_putbackio_readline_from_putback_and_stream_long():
    """
    Test readline for a length longer than the putback buffer
    """
    s = StringIO('one two\nthree four\n')
    s.seek(0)
    p = PutbackInput(s)
    a = p.read(2)
    b = p.read(2)
    p.putback(b)
    p.putback(a)
    assert_equal(p.readline(10), "one two\n")


def test_delimitedio_read():

    s = StringIO('one--two--three')
    s.seek(0)
    p = PutbackInput(s)
    assert_equal(DelimitedInput(p, '--').read(100), 'one')
    assert_equal(DelimitedInput(p, '--').read(100), 'two')
    assert_equal(DelimitedInput(p, '--').read(100), 'three')
    assert_equal(DelimitedInput(p, '--').read(100), '')

    # delimiters are handled correctly, even when they straddle a
    # block (as determined by ``size``)

    s = StringIO('one--two--three')
    s.seek(0)
    p = PutbackInput(s)
    d = DelimitedInput(p, '--')
    assert_equal(d.read(2), 'on')
    assert_equal(d.read(2), 'e')
    assert_equal(d.read(2), '')

def test_delimitedio_readline():

    s = StringIO('one\ntwo|\nthree\n')
    s.seek(0)
    p = PutbackInput(s)
    d = DelimitedInput(p, '|')
    assert_equal(d.readline(), 'one\n')
    assert_equal(d.readline(), 'two')
    assert_equal(d.readline(), '')

    # The case where a newline forms part of the delimiter
    s = StringIO('one\ntwo\n--three\n')
    s.seek(0)
    p = PutbackInput(s)
    d = DelimitedInput(p, '\n--')
    assert_equal(d.readline(), 'one\n')
    assert_equal(d.readline(), 'two')
    assert_equal(d.readline(), '')


