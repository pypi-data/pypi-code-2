#!/usr/bin/env python
# -*- coding: utf-8 -*-

# kvigall: A customizable calender program meant for use in terminals
# Copyright (C) 2010  Niels Serup
# This file is based on "various.py" from Naghni
# <http://metanohi.org/projects/naghni/>

# This file is part of kvigall.
#
# kvigall is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# kvigall is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with kvigall.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## various
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Various minor (but still important) parts
##[ Start date  ]## 2010 August 18

import sys
from threading import Thread
import kvigall.generalinformation as ginfo

exit_messages = ('Goodbye.', 'Farewell.', 'Ciao.', 'Shutting down.',
                 'I have been terminated.', 'So long.', 'Later.')

def error(msg, cont=True, pre=None):
    errstr = str(msg) + '\n'
    if pre is not None:
        errstr = pre + ': ' + errstr
    sys.stderr.write(errstr)
    if cont is not True:
        try:
            sys.exit(cont)
        except Exception:
            sys.exit(1)

def usable_error(msg, cont=True):
    error(msg, cont, ginfo.program_name + ': ')

nothing = lambda *a: None

class Container:
    pass

class Event(Container):
    type=None
    subject=None
    interval=None
    author=None
    projects=None
    text=None


class DefaultingDict(dict):
    """A dict with default values"""
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.default = kwargs.get('default') or []

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            new = self.default[:]
            self.__setitem__(key, new)
            return new

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

