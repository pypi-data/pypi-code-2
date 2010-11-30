# -*- coding: UTF-8 -*-
# vim: fileencoding=UTF-8 filetype=python ff=unix et ts=4 sw=4 sts=4 tw=120
#
# Copyright (c) 2010, Christer Sjöholm -- hcs AT furuvik DOT net
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

from hcs_utils.storage import Storage
from nose.tools import *

def test_init_empty():
    sto = Storage()
    eq_(sto.get_dict(), {})

def test_init_kwargs():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(a=1, b=2)
    eq_(sto.get_dict(), di1)

def test_init_dict():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(di1)
    eq_(id(sto.get_dict()), id(di1))

def test_init_dict_kwargs():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(di1, b=3, c=4)
    eq_(sto.get_dict(), {'a':1, 'b': 3, 'c': 4})
    eq_(id(sto.get_dict()), id(di1))

def test_access():
    di1 = {'a': [1], 'b': [2]}
    sto = Storage(di1)
    eq_(sto.a, [1])
    eq_(sto.b, [2])
    eq_(id(sto.get_dict()['a']), id(sto.a))
    eq_(id(sto.a), id(di1['a']))

@raises(AttributeError)
def test_access_error1():
    sto = Storage()
    _ = sto.a

@raises(KeyError)
def test_access_error2():
    sto = Storage()
    _ = sto['a']

def test_set():
    sto = Storage()
    sto.a = 1
    eq_(sto.a, 1)
    eq_(sto['a'], 1)
    sto.a = 2
    eq_(sto.a, 2)
    eq_(sto['a'], 2)
    sto['a'] = 3
    sto.a = 3

@raises(AttributeError)
def test_del1():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto.a
    sto.a

@raises(AttributeError)
def test_del2():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto['a']
    sto.a

@raises(AttributeError)
def test_del_error1():
    sto = Storage()
    del sto.a

@raises(KeyError)
def test_del_error2():
    sto = Storage()
    del sto['a']

def test_repr():
    sto = Storage(a=1, b=2)
    eq_(repr(sto), "<Storage {'a': 1, 'b': 2}>")

