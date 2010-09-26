r"""
================================================================================
Auto generated by mod2doctest on 2009-11-09 23:47:21.158000
================================================================================

Python 2.6.2 (r262:71605, Apr 14 2009, 22:40:02) [MSC v.1500 32 bit (Intel)] on win32
Type "help", "copyright", "credits" or "license" for more information.


===============================================================================
Test Setup
===============================================================================
>>> import pickle
>>> import os


===============================================================================
Make A List
===============================================================================
>>> alist = [1, -4, 50] + list(set([10, 10, 10]))
>>> alist.sort()
>>> print alist
[-4, 1, 10, 50]


===============================================================================
Pickle The List
===============================================================================
>>> print `pickle.dumps(alist)`
'(lp0\nI-4\naI1\naI10\naI50\na.'


===============================================================================
Add some ellipses
===============================================================================
>>> class Foo(object):
...     pass
... 
>>> print Foo()
<...Foo object at 0x...>
>>> print pickle
<module 'pickle' from '...pickle.pyc'>
>>> os.getcwd()
'...tests'


===============================================================================
This should cause an error
===============================================================================
>>> try:
...     print pickle.dumps(os)
... except TypeError, e:
...     print 'ERROR!', e
... 
ERROR! can't pickle module objects

"""



if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert(src=None, 
                        target=True, 
                        run_doctest=True)    


#===============================================================================
# Test Setup
#===============================================================================
import pickle
import os


#===============================================================================
# Make A List
#===============================================================================
alist = [1, -4, 50] + list(set([10, 10, 10]))
alist.sort()
print alist


#===============================================================================
# Pickle The List
#===============================================================================
print `pickle.dumps(alist)`


#===============================================================================
# Add some ellipses
#===============================================================================
class Foo(object):
    pass

print Foo()
print pickle
os.getcwd()


#===============================================================================
# This should cause an error
#===============================================================================
try:
    print pickle.dumps(os)
except TypeError, e:
    print 'ERROR!', e
