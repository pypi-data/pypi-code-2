"""
Struc is a syntax wrapper for ctypes.Structure

>>> class BYTE(Struc):
...     core = ctypes.c_ubyte

>>> class User(Struc):
...     BYTE.name[32]
...     BYTE.password[32]

>>> class User2(ctypes.Structure):
...     _fields_ = [
...         ('name', ctypes.c_ubyte * 32),
...         ('password', ctypes.c_ubyte * 32),
...     ]

>>> User()._fields_ == User2()._fields_
True

"""

import ctypes


_unbound_fields = []

class StrucMeta(type):

    @staticmethod
    def __new__(cls, name, bases, attrs):
        rv = super(StrucMeta, cls).__new__(cls, name, bases, attrs)

        if not _unbound_fields:
            return rv

        class core(ctypes.Structure):
            _fields_ = _unbound_fields[:]
            del _unbound_fields[:]
        core.__name__ = name
        
        rv.core = core            
        return rv
        
    def __getattr__(self, name):
        _unbound_fields.append((name, self.core))
        return self
        
    def __getitem__(self, index):
        name, core = _unbound_fields.pop()
        _unbound_fields.append((name, core * index))
        return self
        
            
class Struc(object):

    __metaclass__ = StrucMeta

    @staticmethod
    def __new__(cls, *args, **kw):
        return cls.core.__new__(cls.core, *args, **kw)


class BYTE(Struc):
    core = ctypes.c_ubyte
    
    
class WORD(Struc):
    core = ctypes.c_ushort


class DWORD(Struc):
    core = ctypes.c_ulong
    
    
if __name__ == '__main__':
    import doctest
    doctest.testmod()
    


