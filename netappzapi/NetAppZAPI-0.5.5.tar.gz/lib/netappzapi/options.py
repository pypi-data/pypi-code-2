# $Id$
#
##COPYRIGHT##

__revision__ = '$Revision: 1.61 $'

"""
Common options used by NetAppZAPI command line utilities
"""
import optparse
import logging

log = logging.getLogger('zapi')

class BaseOptions(optparse.OptionParser):
    """
    The base options parser class.
    This defines all the base level options and arguments that are
    common to all programs.
    """
    def __init__(self, *args, **kwargs):
        optparse.OptionParser.__init__(self, **kwargs)

        help_debug = "Set the output debug level to: debug, info, warn, error, or critical."

        self.add_option('-u', '--username', dest='username', help="Username on remote filer [%default]", default='root')
        self.add_option('-p', '--password', dest='password', help="Password for remote filer [%default]", default="netapp1")
        self.add_option('-s', '--scheme', dest='scheme', choices=['http', 'https'], help="Connection scheme to use [%default]", default="https")
        self.add_option('', '--debug',         dest='debug', type='choice', choices=('debug', 'info', 'warn', 'error', 'critical'), metavar='LEVEL', default='info', help=help_debug)
        
    def parseOptions(self):
        """
        Emulate the twisted options parser API.
        """
        options, args = self.parse_args()
        self.options = options
        self.args = args

        self.postOptions()

        return self.options, self.args

    def postOptions(self):
        log.setLevel(logging._levelNames.get(self.options.debug.upper(), logging.INFO))
