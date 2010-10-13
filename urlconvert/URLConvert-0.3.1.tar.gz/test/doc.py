# -*- coding: utf8 -*-

"""\
Doctests for paths
"""
#import logging
#logging.basicConfig(level=logging.DEBUG)


import sys; sys.path.append('../')
import doctest
import urlconvert
doctest.testfile('../doc/source/manual.rst', optionflags=doctest.ELLIPSIS)



