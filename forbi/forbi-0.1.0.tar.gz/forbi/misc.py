#!/usr/bin/env python
# -*- coding: utf-8 -*-

# forbi: a TCP-based communication tool
# Copyright (C) 2010  Niels Serup

# This file is part of forbi.
#
# forbi is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# forbi is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General
# Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with forbi. If not, see
# <http://www.gnu.org/licenses/>.

##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Miscellaneous data

# Basic program data
program_name = u'forbi'
program_sender_name = u'forbi-send'
program_description = u'A TCP-based communication tool'
program_sender_description = u'Send messages to foreign forbi clients via a local running client'
version_num = (0, 1, 0)
version_num_text = u'.'.join([unicode(x) for x in version_num])
program_author = u'Niels Serup'
author_email = u'ns@metanohi.org'
version_text = u'''\
%s %s
Copyright (C) 2010  %s
License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.\
''' % (program_name, version_num_text, program_author)

# Basic program functions and classes
import sys
import locale
import datetime
import threading
import subprocess
try:
    from termcolor import colored
except ImportError:
    from forbi.external.termcolor import colored

# Get the system encoding
encoding = locale.getpreferredencoding()
    
def output_text(msg, out, color=None, prefix=''):
    """Output text with or without color, with or without a prefix"""
    if prefix:
        prefix += ': '
    date = datetime.datetime.today().strftime('%T')
    msg = '%s[%s]: %s%s' % (program_name, date, prefix, msg)
    msg = msg.encode(encoding)
    if color:
        msg = colored(msg, color)
    out.write(msg + '\n')

def state(msg, color=True, prefix='', out=sys.stdout):
    """State something"""
    output_text(msg, out, color and 'blue', prefix)
    
def error(msg, color=True, prefix='', out=sys.stderr):
    """Output an error message"""
    output_text(msg, out, color and 'red', prefix)

nothing = lambda *args, **kwargs: None

class TextOutputterBaseFallback(object):
    def state(self, msg, prefix):
        state(msg, False, prefix)

    def error(self, msg, prefix):
        error(msg, False, prefix)

_textoutputter_base_fallback = TextOutputterBaseFallback()
        
class TextOutputter(object):
    """A text outputter"""
    def __init__(self, base=None, prefix=''):
        self.set_textoutputter_base(base)
        self.set_output_prefix(prefix)

    def set_textoutputter_base(self, obj):
        """Set the base object whose functions should be called"""
        self.textoutputter_base = obj or _textoutputter_base_fallback

    def set_output_prefix(self, prefix):
        """Set the output prefix"""
        self.output_prefix = prefix
        
    def state(self, msg):
        """State something via the base object"""
        self.textoutputter_base.state(msg, self.output_prefix)

    def error(self, msg):
        """Output an error message via the base object"""
        self.textoutputter_base.error(msg, self.output_prefix)

class BasicQuickThread(threading.Thread):
    """A quick thread creator and runner"""
    def __init__(self, func, *args, **kwds):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args
        self.kwds = kwds
        self.do_terminate = False
        self.setDaemon(True) # self.daemon = True

    def run(self):
        self.func(*self.args, **self.kwds)

    def terminate(self):
        self.do_terminate = True

class QuickThread(BasicQuickThread):
    """A quicker thread creator and runner"""
    def __init__(self, *args, **kwds):
        BasicQuickThread.__init__(self, *args, **kwds)
        self.start()

class Container(object):
    """A container top class"""

class ForbiError(Exception):
    pass

def exec_program(*args):
    """Run a program in the background"""
    return subprocess.Popen(map(str, args)).pid
