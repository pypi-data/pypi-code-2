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

##[ Name        ]## shadowloss.builtinstickfigures.zorna
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## The human-like "Zorna" stickman
##[ Start date  ]## 2010 September 15

try:
    import shadowloss.stickfigure as stick
except ImportError: # If shadowloss is not installed and this file is
    # run as a stand-alone program, the next line is necessary. It
    # inserts the package base directory into sys.path, making it visible
    import sys, os.path; sys.path.insert(0, os.path.split(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])[0])
    import shadowloss.stickfigure as stick

def create(parent):
    s = stick.StickFigure(parent)
    # Create its limbs
    s.add_line('right knee', 'hip',
               stick.LinearChange((0, 100, 70, 90),
                                  (100, 500, 90, 110),
                                  (500, 1000, 110, 70)),
               lambda info: 20)
    s.add_line(None, 'right knee',
               stick.LinearChange((0, 100, 70, 60),
                                  (100, 500, 60, 110),
                                  (500, 1000, 110, 70)),
               lambda info: 20)
    s.add_line('left knee', 'hip',
               stick.LinearChange((500, 600, 70, 90),
                                  (600, 1000, 90, 110),
                                  (0, 500, 110, 70)),
               lambda info: 20)
    s.add_line(None, 'left knee',
               stick.LinearChange((500, 600, 70, 60),
                                  (600, 1000, 60, 110),
                                  (0, 500, 110, 70)),
               lambda info: 20)
    s.add_line('hip', 'body', lambda info: 85, lambda info: 30)
    s.add_line('body', 'right elbow',
               stick.LinearChange((0, 500, -120, -60),
                                  (500, 1000, -60, -120)),
               lambda info: 13)
    s.add_line('right elbow', None,
               stick.LinearChange((0, 500, -115, 5),
                                  (500, 1000, 5, -115)),
               lambda info: 11)
    s.add_line('body', 'left elbow',
               stick.LinearChange((500, 1000, -120, -60),
                                  (0, 500, -60, -120)),
               lambda info: 13)
    s.add_line('left elbow', None,
               stick.LinearChange((500, 1000, -115, 5),
                                  (0, 500, 5, -115)),
               lambda info: 11)
    s.add_line('body', 'head',
               stick.LinearChange((3, -1, 90),
                                  (3, 0, 90, 50), measure='speed'),
               lambda info: 20, False)
    s.add_line('head', 'eye',
               lambda info: 30,
               lambda info: 7, True)
    s.add_circle('head', lambda info: 12)
    return s

if __name__ == '__main__':
    stick.show_test(create)
