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

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)
doctest.testfile('../doc/source/api.rst', optionflags=doctest.ELLIPSIS)



