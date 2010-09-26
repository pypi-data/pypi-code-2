#===============================================================================
# Test Setup
#===============================================================================
import mod2doctest
from mod2doctest import m2d_print

def fix_output(input):
    return '\n+ '.join(input.replace('>>', '|>').replace('..', '|.').split('\n'))


#===============================================================================
# Test File
#===============================================================================
file = r'''
import sys
import os
print "Current dir is '%s'" % os.getcwd()

'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))


#===============================================================================
# Test Ellipse Memory ID
#===============================================================================
file = r'''
class MyClass(object):
    pass

print MyClass
print MyClass()

'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))


#===============================================================================
# Test Ellipse Traceback
#===============================================================================
file = r'''
import os
import pickle
print pickle.dumps(os)

'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))


#===============================================================================
# Test Shift Comments Left
#===============================================================================
file = r'''
#===============================================================================
# Header
#===============================================================================
# Comment Level 1
## Double Comments
### Triple Comments

'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))


#===============================================================================
# Fix line breaks
#===============================================================================
file = r'''
print 'Only one line break'

print 'Two line breaks'


print 'Six line breaks'





print 'DONE!'
'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))




#===============================================================================
# m2d_print
#===============================================================================
file = r'''
from mod2doctest import m2d_print
#===============================================================================
m2d_print.h1('HEADER 1')
#===============================================================================


m2d_print.h2('HEADER 2')
#-------------------------------------------------------------------------------

'''
print fix_output(mod2doctest.convert(src=file, target=None, 
                                     run_doctest=False, add_testmod=False))


if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert(src=None, 
                        target='selftest_test.py', 
                        run_doctest=True, 
                        add_testmod=True)
    
    