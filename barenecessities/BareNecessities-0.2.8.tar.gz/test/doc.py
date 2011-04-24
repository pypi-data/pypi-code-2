"""\
Doctests for BareNecessities
"""
import doctest
import logging
logging.basicConfig(level=logging.DEBUG)

import sys; sys.path.append('../')
import bn

doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)

