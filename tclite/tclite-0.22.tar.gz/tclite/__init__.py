# -*- coding: utf-8 -*-
'''Object wrapper for tct'''
import os
import sys
import marshal

import tokyo.cabinet as tc

from properties import *


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


class Error(Exception):
    pass


class Model(object):
    __filename__ = None
    key = None
    
    def __init__(self, key=None, _raw_data=None, **kwargs):
        if key is not None:
            self.key = key if isinstance(key, unicode) else key.decode('utf-8')
        self._cached_data = {}
        if _raw_data:
            self._raw_data = _raw_data
        else:
            self._raw_data = {}
            for prop_name, value in kwargs.iteritems():
                if prop_name not in self._properties:
                    raise Error('Unknown field "%s" in model "%s"' % (
                        prop_name, self.__class__.__name__))
                setattr(self, prop_name, value)
    
    def save(self):
        if self.key is None:
            self.key = unicode(self.db.uid())
        self.db[self.key] = self._raw_data
        
    @classmethod
    def get(cls, key):
        key = key if isinstance(key, unicode) else key.decode('utf-8')
        try:
            return cls(key, cls.db[key])
        except KeyError:
            return None
            
    @classmethod
    def filter(cls, operator=None, value=None):
        ret = Filter(cls)
        if operator:
            ret = ret.filter(operator, value)
        return ret

    def delete(self):
        if not self.key:
            raise Error('the object is not saved')
        del self.db[self.key]
        self._raw_data = {}
        self._cached_data = {}

    @class_cached_property
    def db(cls):
        '''Отложенное подключение к бд'''
        if not cls.__filename__:
            raise Error('set __filename__ in model "%s"' % cls.__name__)
        db = tc.TDB()
        db.open(cls.__filename__, tc.HDBOWRITER | tc.HDBOCREAT)
        for prop in (cls.__dict__[n] for n in cls._properties):
            if prop.index:
                if not prop.INDEX:
                    raise Error('field "%s" is not indexed' % prop.__class__.__name__)
                db.setindex(prop.key, prop.INDEX['set'])
            else:
                try:
                    db.setindex(prop.key, tc.TDBITVOID)
                except (tc.Error, AttributeError):
                    pass
        return db
    
    @class_cached_property
    def _properties(cls):
        '''
        {prop_attr_name: save_key_name}
        '''
        ret = {}
        for k, prop in cls.__dict__.items():
            if isinstance(prop, KeyProperty):
                ret[k] = None
            if issubclass(prop.__class__, BaseProperty):
                if not prop.key:
                    prop.key = k
                if prop.key in ret.values():
                    raise Error('multiply key "%s" in model "%s"' % (prop.key, cls.__name__))
                ret[k] = prop.key
        return ret
        
    def __unicode__(self):
        items = []
        for k in ['key'] + self._properties.keys():
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
            items.append((k, v))
        max_len = max([len(k) for k in dict(items).keys()])
        ret = self.__class__.__name__ + '(\n'
        tpl = '    %%-%is = %%s' % max_len
        return ret + ',\n'.join([tpl % (k, v) for k, v in items]) + '\n)'
            
    def __str__(self):
        return self.__unicode__().encode('utf-8')


class Filter(object):
    def __init__(self, model, queue=None, order=None, limit=None):
        self.model = model
        self.queue = queue or []
        self._order = order
        self._limit = limit
    
    def filter(self, operator, value):
        field, condition_abbr = operator.split()
        try:
            prop = self.model.__dict__[field]
        except KeyError:
            raise Error('unknown field: "%s"' % field)
        try:
            condition = prop.get_condition(condition_abbr)
        except KeyError:
            raise Error('unknown condition: "%s" for "%s" field' % (
                condition_abbr, field))
        queue = self.queue[:]
        queue.append((prop.key, condition, prop.dumps(value)))
        return Filter(self.model, queue, self._order, self._limit)
    
    def order(self, field):
        direction = 'asc'
        if field.startswith('-'):
            field = field[1:]
            direction = 'desc'
        try:
            prop = self.model.__dict__[field]
        except KeyError:
            raise Error('unknown field: "%s"' % field)
        try:
            order = (prop.key, prop.get_order(direction))
        except KeyError:
            raise Error('not ordered field: "%s"' % field)
        return Filter(self.model, self.queue, order, self._limit)
        
    def __getitem__(self, key):
        '''Limit'''
        start = 0
        if isinstance(key, slice):
            start = key.start or 0
            if key.stop:
                limit = (key.stop - start, start)
            elif start:
                limit = (-1, start)
        else:
            limit = (1, key)
        return Filter(self.model, self.queue, self._order, limit)

    def _query(self):
        q = self.model.db.query()
        for args in self.queue:
            q.filter(*args)
        if self._order:
            q.sort(*self._order)
        if self._limit:
            q.limit(*self._limit)
        return q

    def __iter__(self):
        for k in self._query().search():
            yield self.model(k, _raw_data=self.model.db[k])
    
    def count(self):
        return len(self._query().search())

    def delete(self):
        self._query().remove()
        
    def get(self):
        for k in self[0]:
            return k
        return None

    def __str__(self):
        return '\nfilters: %s\norder: %s\nlimit: %s' % (
            self.queue, self._order, self._limit)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
