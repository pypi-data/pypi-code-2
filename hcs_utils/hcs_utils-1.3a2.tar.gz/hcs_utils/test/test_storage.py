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

from hcs_utils.storage import Storage, json_load_storage, json_loads_storage, json_dumps_storage
from hcs_utils.unittest import eq_
from py.test import raises

def test_init_empty():
    sto = Storage()
    eq_(sto.get_dict(), {})
    eq_(list(sto), [])

def test_init_kwargs():
    di1 = {'a': 1, 'b': 2}
    sto = Storage(a=1, b=2)
    eq_(sto.get_dict(), di1)
    eq_(list(sto), ['a', 'b'])

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

def test_access_error1():
    sto = Storage()
    with raises(AttributeError):
        _ = sto.a

def test_access_error2():
    sto = Storage()
    with raises(KeyError):
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

def test_contains():
    sto = Storage()
    eq_('a' in sto, False)
    sto.a = 1
    eq_('a' in sto, True)
    del sto.a
    eq_('a' in sto, False)

def test_del1():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto.a
    with raises(AttributeError):
        sto.a

def test_del2():
    sto = Storage()
    sto.a = 1
    sto.a
    del sto['a']
    with raises(AttributeError):
        sto.a

def test_del_error1():
    sto = Storage()
    with raises(AttributeError):
        del sto.a

def test_del_error2():
    sto = Storage()
    with raises(KeyError):
        del sto['a']

def test_repr():
    sto = Storage(a=1, b=2)
    eq_(repr(sto), "<Storage {'a': 1, 'b': 2}>")

def test_json_loads_storage():
    sto = json_loads_storage('[{"a":1}]')
    eq_(sto[0][u'a'], 1)

def test_json_dumps_storage():
    eq_(json_dumps_storage(Storage(a=2)), '{\n  "a": 2\n}')
    eq_(json_dumps_storage([Storage(a=2)]), '[\n  {\n    "a": 2\n  }\n]')
    eq_(json_dumps_storage({'a':2}), '{\n  "a": 2\n}')
