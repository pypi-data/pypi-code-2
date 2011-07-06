"""\
Doctests for FormConvert
"""
import doctest
import logging
logging.basicConfig(level=logging.ERROR)

import sys; sys.path.append('../')
import formbuild

doctest.testmod(formbuild)
doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)

