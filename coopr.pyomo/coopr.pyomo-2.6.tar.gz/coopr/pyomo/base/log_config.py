import sys
import logging
from pyutilib.misc import LogHandler

from os.path import abspath, dirname, join, normpath
coopr_base = normpath(join(dirname(abspath(__file__)), '..', '..', '..'))

logger = logging.getLogger('coopr.pyomo')
logger.setLevel( logging.WARNING )
logger.addHandler( LogHandler(coopr_base, verbosity=lambda: logger.isEnabledFor(logging.DEBUG)) )

