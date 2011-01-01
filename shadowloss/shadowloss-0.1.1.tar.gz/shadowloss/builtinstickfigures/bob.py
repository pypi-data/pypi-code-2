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

##[ Name        ]## shadowloss.builtinstickfigures.bob
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## The standard "Bob" stickman
##[ Start date  ]## 2010 September 15

try:
    import shadowloss.stickfigure as stick
except ImportError: # If shadowloss is not installed and this file is
    # run as a stand-alone program, the next line is necessary. It
    # inserts the package base directory into sys.path, making it visible
    import sys, os.path; sys.path.insert(0, os.path.split(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[0])
    import shadowloss.stickfigure as stick

def create(parent):
    stickfigure = stick.StickFigure(parent)
    # Create its limbs
    stickfigure.add_line(None, 'A',
                         stick.LinearChange((0, 500, 70, 110),
                                            (500, 1000, 110, 70)),
                         lambda info: 40)
    stickfigure.add_line(None, 'A',
                         stick.LinearChange((0, 500, 110, 70),
                                            (500, 1000, 70, 110)),
                         lambda info: 40)
    stickfigure.add_line('A', 'B', lambda info: 90, lambda info: 30)
    stickfigure.add_line('B', None,
                         stick.LinearChange((0, 500, -140, -40),
                                            (500, 1000, -40, -140)),
                         lambda info: 25)
    stickfigure.add_line('B', None,
                         stick.LinearChange((0, 500, -40, -140),
                                            (500, 1000, -140, -40)),
                         lambda info: 25)
    stickfigure.add_line('B', 'C', stick.LinearChange((2, -1, 90),
                                                      (2, 0, 90, 0),
                                                      measure='speed'),
                         lambda info: 20)
    stickfigure.add_circle('C', lambda info: 13)
    stickfigure.add_line('C', 'eye',
               lambda info: 30,
               lambda info: 7, True)
    return stickfigure

if __name__ == '__main__':
    stick.show_test(create)
