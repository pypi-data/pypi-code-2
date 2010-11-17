#!/usr/bin/env python
# -*- coding: utf-8 -*-

# shadowloss: a stickman-oriented game against time
# Copyright (C) 2010  Niels Serup

# This file is part of shadowloss.
#
# shadowloss is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# shadowloss is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with shadowloss.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## shadowloss.various
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Various minor (but still important) parts
##[ Start date  ]## 2010 September 13

import sys
from threading import Thread
import shadowloss.generalinformation as ginfo
try:
    from termcolor import colored
except ImportError:
    from shadowloss.external.termcolor import colored

def error(msg, done=None, pre=None, **kwds):
    errstr = str(msg) + '\n'
    if pre is not None:
        errstr = pre + ': ' + errstr
    if kwds.get('color'):
        errstr = colored(errstr, 'red')
    sys.stderr.write(errstr)
    if done is not None:
        if done in (True, False):
            sys.exit(1)
        else:
            sys.exit(done)

def usable_error(msg, done=None, **kwds):
    error(msg, done, ginfo.program_name + ': ', **kwds)

nothing = lambda *a: None

class Container:
    pass

class thread(Thread):
    """A quick thread creator"""
    def __init__(self, func, *args, **kwds):
        Thread.__init__(self)
        self.func = func
        self.args = args
        self.kwds = kwds
        self.setDaemon(True) # self.daemon = True
        self.start()

    def run(self):
        self.func(*self.args, **self.kwds)

