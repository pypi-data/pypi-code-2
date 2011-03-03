# -*- coding: utf-8 -*-
'''Object wrapper for tct'''
import os
import sys
import marshal

import tokyo.cabinet as tc

from fields import *


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
    '''
    Если у документа нет 

    '''
    __filename__ = None
    key = None
    
    def __init__(self, key=None, _raw_dict=None, **kwargs):
        if key is not None:
            self.key = key if isinstance(key, unicode) else key.decode('utf-8')
        if _raw_dict:
            self._data = _raw_dict
        else:
            self._data = {}
            for prop_name, value in kwargs.iteritems():
                if prop_name not in self._fields:
                    assert 0, 'Unknown field "%s" in model "%s"' % (
                        prop_name, self.__class__.__name__)
                setattr(self, prop_name, value)
    
    def save(self):
        if self.key is None:
            #~ self.key = unicode(len(self.db) + 1)
            self.key = unicode(self.db.uid())
        #~ print 'self.db[%s] = %s' % (self.key, self._data)
        self.db[self.key] = self._data
        
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
            assert 0, 'the object is not saved'
        del self.db[self.key]
        self._data = {}

    @class_cached_property
    def db(cls):
        '''Отложенное подключение к бд'''
        if not cls.__filename__:
            assert 0, 'set __filename__ in model "%s"' % cls.__name__
        db = tc.TDB()
        db.open(cls.__filename__, tc.HDBOWRITER | tc.HDBOCREAT)
        for prop in (cls.__dict__[n] for n in cls._fields):
            #~ print prop.__class__.__name__
            if prop.index:
                #~ print prop.__class__.__name__, prop.INDEX
                if not prop.INDEX:
                    raise Error('field "%s" is not indexed' % prop.__class__.__name__)
                #~ print 'cls.db.setindex(%s, %s)' % (prop.key, prop.INDEX['set'])
                db.setindex(prop.key, prop.INDEX['set'])
            else:
                try:
                    db.setindex(prop.key, tc.TDBITVOID)
                except tc.Error:
                    pass
        return db
    
    @class_cached_property
    def _fields(cls):
        '''
        {prop_attr_name: save_key_name}
        '''
        def rec_bases(cls):
            bases = list(cls.__bases__) or []
            ret = []
            for base in bases:
                for c in rec_bases(base):
                    if c not in ret and c not in bases:
                        ret.append(c)
            ret.extend(bases)
            return ret
        ret = {}
        for k, prop in cls.__dict__.items():
            if BaseField in rec_bases(prop.__class__):
                if not prop.key:
                    prop.key = k
                if prop.key in ret.values():
                    assert 0, 'multiply key "%s" in model "%s"' % (prop.key, cls.__name__)
                ret[k] = prop.key
        return ret
        
    def __unicode__(self):
        items = []
        for k in ['key'] + self._fields.keys():
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
            assert 0, 'unknown field: "%s"' % field
        try:
            condition = prop.get_condition(condition_abbr)
        except KeyError:
            assert 0, 'unknown condition: "%s" for "%s" field' % (
                condition_abbr, field)
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
            assert 0, 'unknown field: "%s"' % field
        try:
            #~ print prop.__class__.__name__, prop.key
            order = (prop.key, prop.get_order(direction))
        except KeyError:
            assert 0, 'not ordered field: "%s"' % field
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
            #~ print 'order:', self._order
            q.sort(*self._order)
        if self._limit:
            q.limit(*self._limit)
        return q

    def __iter__(self):
        for k in self._query().search():
            yield self.model(k, _raw_dict=self.model.db[k])
    
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


class A(Model):
    number      = IntegerField(key='n', index=True)
    fnum        = FloatField()
    name        = UnicodeField(index=True)
    birthday    = DateField(key='b', index=True)
    created     = DateTimeField(index=True)
    #~ tst         = ByteStringField(index=True)
    
    __filename__ = '/home/imbolc/0/var/otct.test.tct'


#~ A.db.clear()

#~ for i in xrange(100):
    #~ A(
        #~ number  = i,
        #~ name    = u'ЫЫЫ',
        #~ fnum    = -1.0 / (i + 1),
        #~ birthday= date(1900 + i, 05, 06),
        #~ created = datetime.now()
    #~ ).save()

#~ print '--- 2'
#~ a.save()
#~ print a

#~ A.db.optimize()
#~ print A.db.uid()

#~ f = A.filter('number >=', 10)
#~ f = f.filter('birthday <', date(1930, 1, 1))
#~ print f.count()
#~ for obj in f.order('fnum'):
#~ for obj in f.order('-number'):
    #~ print obj

#~ f.delete()

#~ a = A.get(6)
#~ print a
#~ a.delete()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
    
