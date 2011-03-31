"""\
Doctests for paths
"""
import logging
logging.basicConfig(level=logging.DEBUG)


import sys; sys.path.append('../')
import doctest
import urlconvert
doctest.testmod(urlconvert)



