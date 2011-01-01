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

##[ Name        ]## shadowloss.stickfigure
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains the class for creating and drawing stick figures
##[ Start date  ]## 2010 September 12

import math

LINE = 1
CIRCLE = 2

class StickFigure(object):
    def __init__(self, parent, offset_x=None, offset_y=None):
        self.parent = parent
        if offset_x is None:
            self.get_offset_x = lambda info: 0
        else:
            self.get_offset_x = offset_x
        if offset_y is None:
            self.get_offset_y = lambda info: 0
        else:
            self.get_offset_y = offset_y
        self.get_offset = lambda info: (self.get_offset_x(info), self.get_offset_y(info))
        self.objects = []
        class Container: pass
        self.info = Container()

    def add_line(self, start, end, angle, length, hidden=False):
        self.objects.append((LINE, start, end, angle, length, not hidden))

    def add_circle(self, pos, radius):
        self.objects.append((CIRCLE, pos, radius))

    def generate_body(self, step=0, speed=1):
        step = step % 1000
        self.info.step = step
        self.info.speed = speed
        offset = self.get_offset(self.info)
        points = {}
        objs = []
        for x in self.objects:
            if x[0] == LINE:
                angle = x[3](self.info)
                start = x[1]
                end = x[2]
                length = x[4](self.info)

                if start is None and end is None:
                    self.parent.error('line not linked to anything, ignoring')
                    continue
                elif start is None:
                    angle = (angle + 180) % 360
                    start, end = end, None
                elif start not in points and end in points:
                    angle = (angle + 180) % 360
                    start, end = end, start

                if start not in points:
                    points[start] = (0, 0)
                angle = math.radians(angle)
                pos = (points[start][0] + length * math.cos(angle),
                       points[start][1] + length * math.sin(angle))
                if end is not None and end not in objs:
                    points[end] = pos
                objs.append((LINE, points[start], pos, x[5]))
            elif x[0] == CIRCLE:
                pos = x[1]
                radius = x[2](step)

                if pos is None:
                    self.parent.error('circle not linked to anything, ignoring')
                    continue
                objs.append((CIRCLE, points[pos], radius))
        smallest = [0, 0]
        for i in range(2):
            smallest[i] = objs[0][1][i]
            for x in objs:
                if x[0] == LINE:
                    for j in range(1, 3):
                        if x[j][i] < smallest[i]:
                            smallest[i] = x[j][i]
                elif x[0] == CIRCLE:
                    if x[1][i] < smallest[i]:
                        smallest[i] = x[1][i]
        new_objs = []
        for x in points.keys():
            points[x] = [points[x][i] - smallest[i] + offset[i] for i
                    in range(2)]
        for x in objs:
            if x[0] == LINE:
                new_objs.append((x[0], [x[1][i] - smallest[i] + offset[i] for i in range(2)],
                                 [x[2][i] - smallest[i] + offset[i]
                                  for i in range(2)], x[3]))
            elif x[0] == CIRCLE:
                new_objs.append((x[0], [x[1][i] - smallest[i] + offset[i] for i in range(2)],
                                 x[2]))
        objs = new_objs
        xs = []
        ys = []
        for x in objs:
            xs.append(x[1][0])
            ys.append(x[1][1])
            if x[0] == LINE:
                xs.append(x[2][0])
                ys.append(x[2][1])

        size = (max(xs) - min(xs), max(ys) - min(ys))
        return objs, points, size

    def draw(self, step=0, speed=1, color=None):
        objs, points, size = self.generate_body(step, speed)
        for x in objs:
            if x[0] == LINE and x[3]:
                self.parent.draw_stickfigure_line(x[1], x[2], size, color)
            elif x[0] == CIRCLE:
                self.parent.draw_stickfigure_circle(x[1], x[2], size, color)
        self.parent.finish_stickfigure_draw()
        return objs, points, size

    def start(self):
        pass

    def end(self):
        pass

class LinearChange(object):
    def __init__(self, *intervals, **kwds):
        measure = kwds.get('measure') or 'step'
        if measure == 'speed':
            self.get_measure = lambda info: info.speed
        else:
            self.get_measure = lambda info: info.step

        intervals = list([list(x) for x in intervals])
        for x in intervals:
            if len(x) == 3:
                x.append(x[2])
        self.intervals = intervals

    def __call__(self, info):
        mea = self.get_measure(info)
        for x in self.intervals:
            a = min(x[:2])
            b = max(x[:2])
            if a != x[0]:
                d, c = x[2], x[3]
            else:
                c, d = x[2], x[3]
            if a == -1:
                if b <= mea:
                    return x[2]
            elif ((a > 0 and mea >= a) or a == 0) and mea < b:
                return ((mea - a) / float(b - a)) * (d - c) + c

        # Else
        return 0

def show_test(func):
    """Shows a simple test run of the stick figure"""

    import sys
    import pygame
    import datetime

    SIZE = (400, 300)
    pygame.display.init()
    SCREEN = pygame.display.set_mode(SIZE)
    pygame.display.set_caption('Stickfigure test')
    bgsurface = pygame.Surface(SIZE).convert()
    bgsurface.fill((0, 0, 0))

    ZOOM = 2
    
    class SimpleSystem(object):
        def error(self, message, done=False):
            print >> sys.stderr, message

        def normalize_point(self, p, rect):
            x = SIZE[0] / 2 + p[0] * ZOOM - rect[0] * ZOOM / 2
            y = SIZE[1] - p[1] * ZOOM
            return int(x), int(y)
 
        def draw_stickfigure_line(self, p1, p2, body_rect,
                                  color=None):
            if not color: color = (255, 255, 255)
            p1 = self.normalize_point(p1, body_rect)
            p2 = self.normalize_point(p2, body_rect)
            pygame.draw.line(SCREEN, color, p1, p2, 3)

        def draw_stickfigure_circle(self, pos, radius, body_rect,
                                    color=None):
            if not color: color = (255, 255, 255)
            pos = self.normalize_point(pos, body_rect)
            pygame.draw.circle(SCREEN, color, pos,
                               int(radius * ZOOM))

        def finish_stickfigure_draw(self):
            # This function may be usable by drawing systems where
            # everything must be drawn at once.
            pass

    stickman = func(SimpleSystem())
    
    SPEED = 1.0
    
    clock = pygame.time.Clock()
    time = 0
    orig_time = datetime.datetime.now()
    prev_time = orig_time
    while not pygame.QUIT in [e.type for e in pygame.event.get()]:
        SCREEN.blit(bgsurface, (0,0))
        objs, points, size = stickman.draw(time, SPEED)
        print points
        pygame.display.flip()

        now = datetime.datetime.now()
        increase = ((now - orig_time) - (prev_time - orig_time)).microseconds / 1000
        time += increase * SPEED
        prev_time = now
        if time >= 999:
            time = time % 1000

        clock.tick(30)

if __name__ == '__main__':
    def create(parent):
        stickman = StickFigure(parent, None, LinearChange((0, 250, 0, 25), (250, 500, 25, 5), (500, 750, 5, 10), (750, 1000, 10, 0)))
        # Create its limbs
        stickman.add_line(None, 'A', LinearChange((0, 500, 70, 110), (500, 1000, 110, 70)), lambda info: 40)
        stickman.add_line(None, 'A', LinearChange((0, 500, 110, 70), (500, 1000, 70, 110)), lambda info: 40)
        stickman.add_line('A', 'B', lambda info: 90, lambda info: 30)
        stickman.add_line('B', None, LinearChange((0, 500, -140, -40), (500, 1000, -40, -140)), lambda info: 25)
        stickman.add_line('B', None, LinearChange((0, 500, -40, -140), (500, 1000, -140, -40)), lambda info: 25)
        stickman.add_line('B', 'C', lambda info: 50 * info.speed, lambda info: 20)
        stickman.add_circle('C', lambda info: 13)
        return stickman

    print 'This is just an example, not a game.'
    show_test(create)
