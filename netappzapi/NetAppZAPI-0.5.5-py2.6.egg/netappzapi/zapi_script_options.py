# $Id$
#
#
# NetAppZAPI - A Python interface to the NetApp ZAPI
# NetAppZAPI is Copyright (c) 2005 Justin Warren <justin@eigenmagic.com>
# NetAppZAPI is licensed under the MIT license
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

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
