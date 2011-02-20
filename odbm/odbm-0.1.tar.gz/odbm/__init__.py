#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Object wrapper for key-value db'''
import os
import zlib
import shutil
import marshal
import time
from datetime import datetime, date


md = marshal.dumps
ml = marshal.loads

class DummyDB(dict):
    def save(self):
        pass

class class_cached_property(object):
    '''
    Кеширующий classmethod
    '''
    def __init__(self, f):
        self.f = f

    def __get__(self, instance, owner):
        value = self.f(owner)
        setattr(owner, self.f.__name__, value)
        return value


class Model(object):
    '''
    >>> class Test(Model):
    ...     __db_type__ = 'dict'
    ...     foo = DateProperty(primary_key=True)
    ...     bar = Property(default=[])
    ...     baz = UnicodeProperty(key='d')
    ...     created = DateTimeProperty(key='c')
    >>> Test(
    ...     foo=date(2000, 01, 02),
    ...     bar=[1, 2], baz=u'ыыы',
    ...     created=datetime.now()
    ... ).save()
    >>> Test(foo=date(1999, 02, 02), created=datetime.now()).save()
    
    >>> Test.get(date(2000, 01, 02)).bar
    [1, 2]
    >>> Test.count()
    2
    >>> Test.count(lambda x: x.baz == u'ыыы')
    1
    >>> [t.foo.year for t in Test.find(
    ...     filter  = lambda x: 3 not in x.bar,
    ...     order   = lambda x: x.foo.year)]
    [1999, 2000]
    >>> Test.find_one().delete()
    >>> Test.count()
    1
    '''
    __filename__ = None
    __db_type__ = 'tc'
    
    def __init__(self, _raw_dict=None, **kwargs):
        if _raw_dict:
            self._data = _raw_dict
        else:
            self._data = {}
            for prop_name, value in kwargs.iteritems():
                if prop_name in self._properties:
                    setattr(self, prop_name, value)
    
    def save(self):
        pk = self._data.pop('__pk__')
        if pk is None:
            assert 0, 'not set primary key "%s" on model "%s"' % (
                self._pk_name, self.__class__.__name__)
        self.db[md(pk)] = md(self._data)
        self._data['__pk__'] = pk
        
    @classmethod
    def get(cls, key):
        key = cls.__dict__[cls._pk_name].encode(key)
        try:
            kw = cls.db[md(key)]
        except KeyError:
            return None
        kw = ml(kw)
        kw['__pk__'] = key
        return cls(kw)
            
    @classmethod
    def find(cls, filter=None, order=None):
        filter = filter or (lambda x: True)
        def filtered():
            for k, v in cls.db.iteritems():
                kw = ml(v)
                kw['__pk__'] = ml(k)
                obj = cls(kw)
                if not filter(obj):
                    continue
                yield obj
        if order:
            order, asc = order if isinstance(order, tuple) else (order, 1)
            items = [(getattr(obj, cls._pk_name), order(obj))
                for obj in filtered()]
            items.sort(key=lambda x: x[1])
            if asc == -1:
                items.reverse()
            return (cls.get(k) for k, v in items)
        else:
            return filtered()

    @classmethod
    def find_one(cls, filter=None, order=None):
        for v in cls.find(filter):
            return v

    @classmethod
    def count(cls, filter=None):
        if not filter:
            return len(cls.db)
        i = 0
        for v in cls.find(filter):
            i += 1
        return i
        
    def delete(self):
        pk = self._data.pop('__pk__')
        if pk is None:
            assert 0, 'not set primary key "%s" on model "%s"' % (
                self._pk_name, self.__class__.__name__)
        del self.db[md(pk)]
        self._data = {}

    @class_cached_property
    def db(cls):
        '''Отложенное подключение к бд'''
        if not cls.__filename__ and cls.__db_type__ != 'dict':
            assert 0, 'set __filename__ in model "%s"' % cls.__name__
        if cls.__db_type__ == 'tc':
            try:
                import tc
            except ImportError:
                import tokyo.cabinet as tc
            import tokyo.cabinet as tc
            ret = tc.HDB()
            ret.open(cls.__filename__, tc.HDBOWRITER | tc.HDBOCREAT)
            return ret
        elif cls.__db_type__ == 'fdb':
            import om.fdb
            return om.fdb.FDB(cls.__filename__)
        elif cls.__db_type__ == 'gdbm':
            import gdbm
            return gdbm.open(cls.__filename__, 'c')
        elif cls.__db_type__ == 'dict':
            return DummyDB()
        assert 0, 'this db is not supported'
    
    @class_cached_property
    def _pk_name(cls):
        ret = [k for k, v in cls._properties.iteritems() if v == '__pk__']
        if not ret:
            assert 0, 'primary key in model "%s" not found' % cls.__name__
        return ret[0]
    
    @class_cached_property
    def _properties(cls):
        '''
        {prop_attr_name: save_key_name}
        '''
        ret = {}
        for k, prop in cls.__dict__.iteritems():
            if BaseProperty in prop.__class__.__bases__:
                if not prop.key:
                    prop.key = k
                if prop.key in ret.values():
                    keyname = 'primary key' if prop.key == '__pk__' else 'key "%s"' % prop.key
                    assert 0, 'multiply %s in model "%s"' % (keyname, cls.__name__)
                ret[k] = prop.key
        return ret
        
    def __unicode__(self):
        keys = self._properties.keys()
        values = {}
        for k in keys:
            v = getattr(self, k)
            if isinstance(v, str):
                v = "'%s'" % v
            if isinstance(v, unicode):
                v = "u'%s'" % v
            try:
                v = unicode(v)
                if len(v) > 50:
                    v = v[:50] + ' ...'
            except UnicodeDecodeError:
                v = '- not printable -'
            if k == self._pk_name:
                k += ' (pk)'
            values[k] = v
        max_len = max([len(k) for k in values.keys()])
        ret = self.__class__.__name__ + '(\n'
        tpl = '    %%-%is = %%s' % max_len
        return ret + '\n'.join([tpl % (k, values[k]) for k in values.keys()]) + '\n)'
            
    def __str__(self):
        return self.__unicode__().encode('utf-8')


class BaseProperty(object):
    def __init__(self, key=None, default=None, primary_key=False):
        self.key = '__pk__' if primary_key else key
        self.default = default
        self.primary_key = primary_key
        
    def __get__(self, instance, owner):
        if self.key in instance._data:
            return self.decode(instance._data[self.key])
        return self.default
        
    def __set__(self, instance, value):
        instance._data[self.key] = self.encode(value)
        
    def __delete__(self, instance):
        del instance._data[self.key]
    
    def encode(self, value):
        '''Приведение к маршализируемому типу'''
        return value
        
    def decode(self, value):
        '''Из маршализируемого типа'''
        return value


class Property(BaseProperty):
    pass


class UnicodeProperty(BaseProperty):
    def encode(self, value):
        return unicode(value)
    def decode(self, value):
        return value


class DateTimeProperty(BaseProperty):
    def encode(self, value):
        return time.mktime(value.timetuple()) + value.microsecond / 1000000.0
    def decode(self, value):
        return datetime.fromtimestamp(value)


class DateProperty(BaseProperty):
    def encode(self, value):
        return int(time.mktime((
            value.year, value.month, value.day, 0, 0, 0, 0, 0, 0)))
    def decode(self, value):
        return date.fromtimestamp(value)



if __name__ == "__main__":
    import doctest
    doctest.testmod()
