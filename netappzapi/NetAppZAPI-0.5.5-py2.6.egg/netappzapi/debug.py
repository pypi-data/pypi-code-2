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

__version__ = '$Revision: 1.28 $'

import logging
import logging.handlers
import sys

#FORMAT = "%(asctime)s %(levelname)7s [%(thread)x] (%(module)s) %(message)s"
#FORMAT = "%(asctime)s %(levelno)2s (%(module)s) %(message)s"        
FORMAT = "%(asctime)s %(levelname)7s: %(message)s"
formatter = logging.Formatter(FORMAT, '%Y-%m-%d %H:%M:%S')

stdoutHandler = logging.StreamHandler(sys.stdout)
stdoutHandler.setFormatter(formatter)

class LocalLogger(logging.Logger):
    
    def __init__(self, name):
        level = logging.INFO
        logging.Logger.__init__(self, name, level)
        self.addHandler(stdoutHandler)
        return
    pass

def add_file_handler(filename):
    handler = logging.handlers.RotatingFileHandler(filename=filename, maxBytes=10e6, backupCount=10)
    handler.setFormatter(formatter)
    log = logging.getLogger('zapi')
    log.addHandler(handler)
    
logging.setLoggerClass(LocalLogger)
