"""\
Doctests for StringConvert

For the tests to work you'll need to install ConversionKit and PyDNS:

::

    $ easy_install ConversionKit PyDNS

Some ISPs block MX and A record lookups so you may find the DNS lookups
fail on your local machine in which case you'll have to run the test on
a remote server.
"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)

try:
    import DNS
except:
    print 
    print 'WARNING: You do not have PyDNS installed so two of the tests'
    print 'are likely to have failed.'
    print 
    print 'Install PyDNS like this: easy_install PyDNS'




