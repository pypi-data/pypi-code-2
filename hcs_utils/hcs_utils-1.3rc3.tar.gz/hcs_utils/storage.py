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

from __future__ import absolute_import

import collections
import json


class Storage(object):
    """
    A Storage object wraps a dictionary.
    In addition to `obj['foo']`, `obj.foo` can also be used for accessing
    values.

    Wraps the dictionary instead of extending it so that the number of names
    that can conflict with keys in the dict is kept minimal.

        >>> o = Storage(a=1)
        >>> o.a
        1
        >>> o['a']
        1
        >>> 'a' in o
        True
        >>> o.a = 2
        >>> o['a']
        2
        >>> del o.a
        >>> o.a
        Traceback (most recent call last):
            ...
        AttributeError: 'a'

        Based on Storage in web.py (public domain)
    """
    __internal_vars = ('_dict', '_case_insensitive')

    def __init__(self, dict_=None, default_factory=None,
            case_insensitive=False, **kwargs):
        '''
        dict_: Dict to use as backend for Storage object.
        case_insensitive: All given keys will be converted to lower case before
                          trying to set/access the dict. If a populated dict_
                          is given it must already have all keys in lower case.
        default_factory: if dict_ is None and default_factory is set then a
                         defaultdict will be used with the specified
                         default_factory.

        '''
        if dict_ != None:
            self._dict = dict_
            self._dict.update(kwargs)
        elif default_factory:
            self._dict = collections.defaultdict(default_factory, **kwargs)
        else:
            self._dict = dict(**kwargs)
        self._case_insensitive = case_insensitive

    def get_dict(self):
        ''' Get the contained dict.'''
        return self._dict

    def __getattr__(self, key):
        try:
            # prevent recursion (triggered by pickle.load()
            if key in Storage.__internal_vars:
                raise AttributeError('No such attribute')
            return self[key]
        except KeyError as err:
            raise AttributeError(err)

    def __setattr__(self, key, value):
        # prevent recursion (triggered by pickle.load()
        if key in Storage.__internal_vars:
            object.__setattr__(self, key, value)
        else:
            self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as err:
            raise AttributeError(err)

    # For container methods pass-through to the underlying dict.
    def __getitem__(self, key):
        if self._case_insensitive:
            key = key.lower()
        return self._dict[key]

    def __setitem__(self, key, value):
        if self._case_insensitive:
            key = key.lower()
        self._dict[key] = value

    def __delitem__(self, key):
        if self._case_insensitive:
            key = key.lower()
        del self._dict[key]

    def __contains__(self, key):
        if self._case_insensitive:
            key = key.lower()
        return key in self._dict

    def __iter__(self):
        return self._dict.__iter__()

    def __len__(self):
        return self._dict.__len__()

    def __eq__(self, other):
        return isinstance(other, Storage) and self._dict == other._dict

    def __repr__(self):
        items = []
        if self._case_insensitive:
            items.append('case_insensitive=True')
        if isinstance(self._dict, collections.defaultdict):
            items.append(
                    'default_factory={0}'.format(self._dict.default_factory))
        items.extend('{0}={1}'.format(i[0], repr(i[1])) for i in
                sorted(self._dict.items()))
        return '{0}({1})'.format(self.__class__.__name__, ', '.join(items))


def json_loads_storage(str_):
    '''
        >>> json_loads_storage('[{"a":1}]')
        [Storage(a=1)]
    '''
    return json.loads(str_, object_hook=Storage)


def json_load_storage(fp_):
    return json.load(fp_, object_hook=Storage)


def json_dumps_storage(job):
    '''
        >>> json_dumps_storage(Storage(a=2))
        '{\\n  "a": 2\\n}'
        >>> json_dumps_storage([Storage(a=2)])
        '[\\n  {\\n    "a": 2\\n  }\\n]'
        >>> json_dumps_storage({'a':2})
        '{\\n  "a": 2\\n}'
    '''
    return json.dumps(job, default=_storage_to_dict, indent=2)


def json_dump_storage(obj, fp_):
    return json.dump(obj, fp_, default=_storage_to_dict, indent=2)


def _storage_to_dict(obj):
    '''
        >>> _storage_to_dict(Storage(a=1))
        {'a': 1}
        >>> _storage_to_dict('')
        Traceback (most recent call last):
        ...
        TypeError: not a Storage object

    '''
    if isinstance(obj, Storage):
        return obj.get_dict()
    else:
        raise TypeError('not a Storage object')


def unicode_storage(storage):
    '''Convert all values in storage to unicode and assert that all keys
    can be converted'''
    for key in storage:
        _ = unicode(key)  # just check that it can be done
        storage[key] = unicode(storage[key])
    return storage
