if __name__ == '__main__':
    import mod2doctest
    mod2doctest.convert(src=None, 
                        target='m2dprintexample_test.py', 
                        run_doctest=True, 
                        add_testmod=True)
    
from mod2doctest import m2d_print


#===============================================================================
m2d_print.h1('TEST_SETUP')
#===============================================================================
import pickle
import os


#===============================================================================
m2d_print.h1('TEST_TEARDOWN')
#===============================================================================
import sys
del sys.modules['pickle']
print sys.modules.keys()


m2d_print.h2('GOING TO DO IT')
#-------------------------------------------------------------------------------
print 'foobar'


m2d_print.h2('GOING TO DO IT')
#-------------------------------------------------------------------------------
print 'baz'


m2d_print.h3('NOW YOU WILL SEE IT')
print 'foobarbaz'
