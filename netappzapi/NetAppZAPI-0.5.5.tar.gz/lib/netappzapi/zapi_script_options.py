# $Id$
#
##COPYRIGHT##

__revision__ = '$Revision: 1.61 $'

"""
Options used by the zapi commandline scripts. Quite minimal.
"""
from options import BaseOptions

import logging
import debug
from twisted.python import log as tlog

log = logging.getLogger('modipy')

class ZAPIScriptOptions(BaseOptions):

    def __init__(self, *args, **kwargs):
        """
        Initialise a base level options parser.
        """
        optparse.OptionParser.__init__(self, **kwargs)
    
        help_debug = "Set the output debug level to: debug, info, warn, error, or critical."

    def addOptions(self):
        """
        Override this method in subclasses to add more options.
        This enables multiple inheritence from the common base class.
        """
        pass
        
    def parseOptions(self, argv=sys.argv[1:]):
        """
        Emulate the twisted options parser API.
        """
        options, args = self.parse_args(argv)
        self.options = options
        self.args = args
        self.postOptions()

    def postOptions(self):
        """
        Perform post options parsing operations.
        """
        # Set standard logging level
        log.setLevel(logging._levelNames.get(self.options.debug.upper(), logging.INFO))
