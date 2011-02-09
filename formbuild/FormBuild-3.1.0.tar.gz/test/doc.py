"""\
Doctests for FormConvert
"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')
import formbuild

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)
doctest.testmod(formbuild)

