"""\
Doctests for ConversionKit

You'll need to install FormEncode for the compatibility tests:

::

    easy_install FormEncode

"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')
import conversionkit

doctest.testfile('../doc/source/formencode.rst', optionflags=doctest.ELLIPSIS)



