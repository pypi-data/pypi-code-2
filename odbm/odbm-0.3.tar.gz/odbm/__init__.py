#!/usr/bin/python
# -*- coding: utf-8 -*-
'''Object wrapper for key-value db'''
import os
import sys
import marshal
import time
from datetime import datetime, date


md = marshal.dumps
ml = marshal.loads

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
    ...     day     = DateProperty(primary_key=True)
    ...     foo     = Property(default=[1, 2])
    ...     ustr    = UnicodeProperty(key='u')
    ...     cstr    = CompressedStringProperty()
    ...     cuni    = CompressedUnicodeProperty() 
    ...     cdump   = CompressedProperty(default={}) 
    ...     created = DateTimeProperty(key='c')
    ...
    ...     __db_type__ = 'dict'
    
    >>> Test(
    ...     day     = date(2000, 01, 02),
    ...     foo     = [1, u'ы', {'a': 'b'}],
    ...     ustr    = u'ыыы',
    ...     cstr    = 'A' * 1000,
    ...     cuni    = u'Ы' * 1000,
    ...     cdump   = range(10),
    ...     created = datetime.now(),
    ... ).save()
    >>> Test(day=date(1999, 02, 02)).save()
    
    >>> Test.get(date(1999, 02, 02)).foo
    [1, 2]
    
    >>> Test.count()
    2
    >>> Test.count(lambda x: x.ustr == u'ыыы')
    1
    
    >>> [t.day.year for t in Test.find(
    ...     filter  = lambda x: 3 not in x.foo,
    ...     order   = lambda x: x.day)]
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
        pk = self._data.pop('__pk__', None)
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
        elif cls.__db_type__ == 'kc':
            import kyotocabinet as kc
            ret = kc.DB()
            ret.open("var/test.kch", db.OWRITER | db.OCREATE)
            return ret
        elif cls.__db_type__ == 'fsdbm':
            import fsdbm
            return fsdbm.FSDBM(cls.__filename__)
        elif cls.__db_type__ == 'gdbm':
            import gdbm
            return gdbm.open(cls.__filename__, 'c')
        elif cls.__db_type__ == 'dict':
            return DictDBM(cls.__filename__)
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
        def req_bases(cls):
            bases = list(cls.__bases__) or []
            ret = []
            for base in bases:
                for c in req_bases(base):
                    if c not in ret and c not in bases:
                        ret.append(c)
            ret.extend(bases)
            return ret        
        ret = {}
        for k, prop in cls.__dict__.iteritems():
            if BaseProperty in req_bases(prop.__class__):
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


class CompressedStringProperty(BaseProperty):
    def __init__(self, compressor='zlib', compress_level=9, *args, **kwargs):
        __import__(compressor)
        self.compressor = sys.modules[compressor]
        self.compress_level = compress_level
        super(CompressedStringProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        return self.compressor.compress(value, self.compress_level)
    def decode(self, value):
        return self.compressor.decompress(value)


class CompressedUnicodeProperty(CompressedStringProperty):
    def __init__(self, internal_encoding='utf-8',
                encoding_errors='ignore', *args, **kwargs):
        self.internal_encoding = internal_encoding
        self.encoding_errors = encoding_errors
        super(CompressedUnicodeProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        value = value.encode(self.internal_encoding, self.encoding_errors)
        return super(CompressedUnicodeProperty, self).encode(value)
    def decode(self, value):
        value = super(CompressedUnicodeProperty, self).decode(value)
        return value.decode(self.internal_encoding, self.encoding_errors)


class CompressedProperty(CompressedStringProperty):
    def __init__(self, dumper='marshal', *args, **kwargs):
        __import__(dumper)
        self.dumper = sys.modules[dumper]
        super(CompressedProperty, self).__init__(*args, **kwargs)
    def encode(self, value):
        value = self.dumper.dumps(value)
        return super(CompressedProperty, self).encode(value)
    def decode(self, value):
        value = super(CompressedProperty, self).decode(value)
        return self.dumper.loads(value)


class DictDBM(dict):
    '''Dummy dbm for tests'''
    def __init__(self, filename=None):
        self.filename = filename
        if filename:
            try:
                super(self.__class__, self).__init__(
                    **marshal.load(open(filename)))
            except IOError:
                pass
    
    def __setitem__(self, key, value):
        super(self.__class__, self).__setitem__(key, value)
        self.save()
        
    def clear(self):
        super(self.__class__, self).clear()
        self.save()
        
    def save(self):
        if self.filename:
            marshal.dump(dict(self), open(self.filename, 'w'))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
