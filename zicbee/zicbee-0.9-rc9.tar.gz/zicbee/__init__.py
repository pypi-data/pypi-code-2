"""
.. moduleauthor:: Fabien Devaux

Zicbee core engine version |version|, using :mod:`zicbee_lib` extensively
"""

try:
    import zicbee_lib.debug # init logging
except ImportError:
    print "I hope this is just build time..."
__version__ = '0.9-rc9' # next is 0.9-rc9
