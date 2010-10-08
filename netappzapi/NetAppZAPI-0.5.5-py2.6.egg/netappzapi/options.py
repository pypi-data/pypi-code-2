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
