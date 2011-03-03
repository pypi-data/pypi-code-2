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


class BaseField(object):
    INDEX = {}
    CONDITION_TYPE = 'str'
    
    def __init__(self, key=None, default=None, index=False):
        self.key = key
        self.default = default
        self.index = index

    def __get__(self, instance, owner):
        if self.key in instance._data:
            return self.loads(instance._data[self.key])
        return self.default

    def __set__(self, instance, value):
        instance._data[self.key] = self.dumps(value)
        
    def __delete__(self, instance):
        del instance._data[self.key]
        
    def get_condition(self, abbr):
        return CONDITIONS.get(self.CONDITION_TYPE, {})[abbr]
        
    def get_order(self, direction):
        return self.INDEX[direction]
    
    def dumps(self, value):
        return value

    def loads(self, s):
        return s


class ByteStringField(BaseField):
    INDEX = INDEX_STR


class UnicodeField(BaseField):
    '''
        >>> value = 'эээ'.decode('utf-8')
        >>> obj = UnicodeField()
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
        super(UnicodeField, self).__init__(*args, **kwargs)
        
    def dumps(self, value):
        return value.encode(self.internal_encoding, self.encoding_errors)
        
    def loads(self, s):
        return s.decode(self.internal_encoding, self.encoding_errors)


class IntegerField(BaseField):
    '''
        >>> value = 10
        >>> obj = IntegerField()
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


class FloatField(BaseField):
    '''
        >>> value = 10.11
        >>> obj = FloatField()
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


class BooleanField(BaseField):
    '''
        >>> value = True
        >>> obj = BooleanField()
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


class DateField(BaseField):
    '''
        >>> value = date.today()
        >>> obj = DateField()
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


class DateTimeField(BaseField):
    '''
        >>> value = datetime.now()
        >>> obj = DateTimeField()
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


class DumpField(BaseField):
    '''
        >>> value = [1, {'a': False}]
        >>> obj = DumpField()
        >>> dump = obj.dumps(value)
        >>> isinstance(dump, str)
        True
        >>> obj.loads(dump) == value
        True
    '''
    def __init__(self, dumper='marshal', *args, **kwargs):
        __import__(dumper)
        self.dumper = sys.modules[dumper]
        super(DumpField, self).__init__(*args, **kwargs)
    
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
            value = self.compressor.compress(value, self.compress_level)
            return super(self.__class__, self).dumps(value)
            
        def loads(self, s):
            s = self.compressor.decompress(s)
            return super(self.__class__, self).loads(value)
            
    Ret.__name__ = 'Compressed' + cls.__name__
    return Ret

CompressedByteStringField = _compressed_factory(ByteStringField)
CompressedUnicodeField = _compressed_factory(UnicodeField)
CompressedDumpField = _compressed_factory(DumpField)


if __name__ == "__main__":
    import doctest
    doctest.testmod()