#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Naghni: a breath-taking side-scroller focusing on round lifeforms
# Copyright (C) 2010  Niels Serup, based on statusprinter.py from
# Dililatum <http://metanohi.org/projects/dililatum/>

# This file is part of Naghni.
#
# Naghni is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Naghni is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Naghni.  If not, see <http://www.gnu.org/licenses/>.

##[ Name        ]## statusprinter
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Prints statuses with different prefixes
##[ Start date  ]## 2010 July 14

from datetime import datetime
import sys

try:
    from termcolor import colored
    def withcolor(msg, fg, bg):
        nmsg = ''
        spl = msg.split('\n')
        while spl[-1] == '':
            spl.pop()
        nmsg = colored(spl[0], fg, 'on_' + bg, attrs=['bold']) + '\n'
        nmsg += '\n'.join(spl[1:]) + '\n'

        return nmsg + '\n'
except Exception:
    def withcolor(msg, fg, bg):
        return msg + '\n'

def atleast(m, r):
    if r < m:
        return m
    else:
        return r

class StatusPrinter(object):
    def __init__(self, world, name, fgcolor='black', bgcolor='white',
                 outfile=sys.stdout):
        self.world = world
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.outfile = outfile
        self.header = '####' + name[:10] + \
            atleast(0, 10 - len(name) + 4) * '#' + '%s####'
        self.simpleheader = name + ':%s:'

    def __call__(self, msg):
        if self.world.term_simpleprint:
            msg = self.simpleheader % datetime.now() + '\n' + msg + '\n'
            self.outfile.write(msg)
        else:
            msg = self.header % datetime.now() + '\n' + msg + '\n'
            if self.world.term_verbose:
                if self.world.term_colorprint:
                    self.outfile.write(withcolor(msg, self.fgcolor,
                                                 self.bgcolor))
                else:
                    self.outfile.write(msg + '\n')

