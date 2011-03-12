# -*- coding: utf-8 -*-
import sys
import struct
import time
from datetime import datetime, date

import tokyo.cabinet as tc


INDEX_STR = {'set': tc.TDBITLEXICAL, 'asc': tc.TDBQOSTRASC,
            'desc': tc.TDBQOSTRDESC}
INDEX_NUM = {'set': tc.TDBITDECIMAL, 'asc': tc.TDBQONUMASC,
            'desc': tc.TDBQONUMDESC}    
CONDITIONS = {
    'str': {
        '=' : tc.TDBQCSTREQ,
        'in' : tc.TDBQCSTRINC,
        'startswith' : tc.TDBQCSTRBW,
        'endswith' : tc.TDBQCSTREW,
    },
    'num': {
        '=' : tc.TDBQCNUMEQ,
        '>' : tc.TDBQCNUMGT,
        '>=' : tc.TDBQCNUMGE,
        '<' : tc.TDBQCNUMLT,
        '<=' : tc.TDBQCNUMLE,
    },
}    


class KeyProperty(object):
    index = False
    
    def __get__(self, instance, owner):
        return instance.key

    def __set__(self, instance, value):
        instance.key = value if isinstance(value, unicode) else value.decode('utf-8')


class BaseProperty(object):
    INDEX = {}
    CONDITION_TYPE = 'str'
    
    def __init__(self, key=None, default=None, index=False):
        self.key = key
        self.default = default
        self.index = index

    def __get__(self, instance, owner):
        if self.key in instance._cached_data:
            return instance._cached_data[self.key]
        if self.key in instance._raw_data:
            ret = self.loads(instance._raw_data[self.key])
            instance._cached_data[self.key] = ret
            return ret
        return self.default

    def __set__(self, instance, value):
        instance._cached_data[self.key] = value
        instance._raw_data[self.key] = self.dumps(value)
        
    def __delete__(self, instance):
        del instance._raw_data[self.key]
        if self.key in instance._cached_data:
            del instance._cached_data[self.key]
        
    def get_condition(self, abbr):
        return CONDITIONS.get(self.CONDITION_TYPE, {})[abbr]
        
    def get_order(self, direction):
        return self.INDEX[direction]
    
    def dumps(self, value):
        return value

    def loads(self, s):
        return s


class ByteStringProperty(BaseProperty):
    INDEX = INDEX_STR


class UnicodeProperty(BaseProperty):
    '''
        >>> value = 'эээ'.decode('utf-8')
        >>> obj = UnicodeProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_STR
    
    def __init__(self, internal_encoding='utf-8',
                encoding_errors='ignore', *args, **kwargs):
        self.internal_encoding = internal_encoding
        self.encoding_errors = encoding_errors
        super(UnicodeProperty, self).__init__(*args, **kwargs)
        
    def dumps(self, value):
        return value.encode(self.internal_encoding, self.encoding_errors)
        
    def loads(self, s):
        return s.decode(self.internal_encoding, self.encoding_errors)


class IntegerProperty(BaseProperty):
    '''
        >>> value = 10
        >>> obj = IntegerProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_NUM
    CONDITION_TYPE = 'num'
    
    def dumps(self, value):
        return str(value)
    
    def loads(self, s):
        return int(s)


class FloatProperty(BaseProperty):
    '''
        >>> value = 10.11
        >>> obj = FloatProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_NUM
    CONDITION_TYPE = 'num'
    
    def dumps(self, value):
        return '%f' % value
    
    def loads(self, s):
        return float(s)


class BooleanProperty(BaseProperty):
    '''
        >>> value = True
        >>> obj = BooleanProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_NUM
    CONDITION_TYPE = 'num'
    
    def dumps(self, value):
        return str(int(value))
    
    def loads(self, s):
        return bool(int(s))


class DateProperty(BaseProperty):
    '''
        >>> value = date.today()
        >>> obj = DateProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_NUM
    CONDITION_TYPE = 'num'
    
    def dumps(self, value):
        return '%i%02i%02i' % (value.year, value.month, value.day)

    def loads(self, s):
        return date(int(s[:-4]), int(s[-4:-2]), int(s[-2:]))


class DateTimeProperty(BaseProperty):
    '''
        >>> value = datetime.now()
        >>> obj = DateTimeProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    INDEX = INDEX_NUM
    CONDITION_TYPE = 'num'
    
    def dumps(self, value):
        ms = '' if value.microsecond else '000000'
        return value.isoformat().translate(None, 'T-:.') + ms

    def loads(self, s):
        return datetime(int(s[:-16]), int(s[-16:-14]), int(s[-14:-12]),
            int(s[-12:-10]), int(s[-10:-8]), int(s[-8:-6]), int(s[-6:]))


class DumpProperty(BaseProperty):
    '''
        >>> value = [1, {'a': False}]
        >>> obj = DumpProperty()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    def __init__(self, dumper='marshal', *args, **kwargs):
        __import__(dumper)
        self.dumper = sys.modules[dumper]
        super(DumpProperty, self).__init__(*args, **kwargs)
    
    def dumps(self, value):
        return self.dumper.dumps(value)

    def loads(self, s):
        return self.dumper.loads(s)


def _compressed_factory(cls):
    class Ret(cls):
        INDEX = {}
        CONDITION_TYPE = 'str'
        
        def __init__(self, compressor='zlib', compress_level=9, *args, **kwargs):
            __import__(compressor)
            self.compressor = sys.modules[compressor]
            self.compress_level = compress_level
            super(self.__class__, self).__init__(*args, **kwargs)
            
        def dumps(self, value):
            value = super(self.__class__, self).dumps(value)
            return self.compressor.compress(value, self.compress_level)
            
        def loads(self, s):
            s = self.compressor.decompress(s)
            return super(self.__class__, self).loads(s)
            
    Ret.__name__ = 'Compressed' + cls.__name__
    return Ret

CompressedByteStringProperty = _compressed_factory(ByteStringProperty)
CompressedUnicodeProperty = _compressed_factory(UnicodeProperty)
CompressedDumpProperty = _compressed_factory(DumpProperty)


if __name__ == "__main__":
    import doctest
    doctest.testmod()