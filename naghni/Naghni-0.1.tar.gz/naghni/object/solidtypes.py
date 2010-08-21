#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Naghni: a breath-taking side-scroller focusing on round lifeforms
# Copyright (C) 2010  Niels Serup

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

##[ Name        ]## solidtypes
##[ Maintainer  ]## Niels Serup <ns@metanohi.org>
##[ Description ]## Contains classes for different types of solids,
                  # detailing the purposes instead of the looks
##[ Start date  ]## 2010 August 14

import math
import naghni.various as various

class SolidType:
    def __init__(self, parent):
        self.parent = parent
        self.level = self.parent.level
        self.back = self.parent.back
        self.world = self.level.world
        self.orig = various.Container()
        self.orig.update = self.parent.update
        self.orig.action = self.parent.action
        self.orig.draw = self.parent.draw
        self.init()

    def init(self):
        pass

    def update(self):
        self.orig.update()

    def action(self):
        self.orig.action()

    def draw(self, **kargs):
        self.orig.draw(**kargs)

class Edible(SolidType):
    def init(self):
        self.disappearing = False

    def action(self):
        self.parent.bounce_off = False
        self.parent.collides = various.nothing
        self.disappearing = True
        self.gone = 0.0
        self.mass = self.parent.get_mass()

    def update(self):
        if not self.disappearing:
            return

        more_gone = 1.0 / self.world.current_fps
        self.gone += more_gone
        if self.gone > 1:
            more_gone -= self.gone - 1
            self.gone = 1
        current_mass = self.mass * more_gone
        self.parent.color = self.parent.color_from_density(self.gone * 0.6 + 0.4)
        self.level.main_solid.add_mass(current_mass, self.parent.density)
        if self.gone == 1:
            self.level.solids.remove(self.parent)
            return

class Hole(SolidType):
    def init(self):
        self.parent.bounce_off = False
        self.ocolor = self.back.create.color(255, 255, 255, 0)
        self.border_color = self.back.create.color(0, 0, 0)
        self.orig_mass = self.parent.get_area() * self.parent.density
        self.orig_mass_alpha = self.parent.get_area() * self.parent.density / 255

    def action(self):
        s_area = self.parent.get_area()
        s_mass = s_area * self.parent.density
        orig_main_mass = self.level.main_solid.get_mass()

        c_mass = 0
        r = 2000.0
        while c_mass < 500:
            m_mass = r * self.level.main_solid.density / \
                self.world.current_fps
            c_mass = orig_main_mass - m_mass
            if r < 500.0:
                return
            r -= 100.0

        n_mass = s_mass - m_mass
        if n_mass <= 0:
            self.level.solids.remove(self.parent)
            done = True
            for x in self.level.solids:
                if x.type == Hole:
                    done = False
                    break
            if done:
                self.level.end()
            return
        self.parent.density = n_mass / s_area
        self.parent.color = self.parent.color_from_density()
        self.ocolor = self.back.create.color(
            255, 255, 255, int((self.orig_mass - n_mass) / self.orig_mass_alpha))
        self.level.main_solid.add_mass(-m_mass, self.level.main_solid.density)

    def draw(self):
        m_color = self.parent.color.mix_color(self.ocolor)
        self.orig.draw(color=m_color, border=self.border_color,
                       borderwidth=5*self.world.zoom)

class Ground(SolidType):
    pass

class Air(SolidType):
    def init(self):
        self.parent.bounce_off = False

class Character(SolidType):
    # Only circles can be characters right now

    def init(self):
        self.status = 3
        self.parent.collides = various.nothing

    def set_speed_after_angle(self, *angle):
        e_angle = [self.get_exit_angle(x) for x in angle]
        speed_len = self.parent.get_speed()
        self.parent.speed = [0, 0]
        f = 0.5 / len(e_angle)
        for a in e_angle:
            self.parent.speed[0] += speed_len * math.cos(a) * f
            self.parent.speed[1] += speed_len * math.sin(a) * f

        sangle = self.parent.get_angle()
        angle = sum(angle) / len(angle)

        rev = angle - math.pi
        if (angle - sangle) % (math.pi * 2) > \
                (rev - sangle) % (math.pi * 2):
            e = math.radians(90)
        else:
            e = -math.radians(90)
        b = angle + e

        # Make it bounce outwards, coming from the angle of the line
        # it's bouncing from
        r = math.sqrt(self.parent.radius) # How much extra speed
        espeed = [r * math.cos(b), r * math.sin(b)]
        if math.cos(abs(sangle - b)) * self.parent.get_speed() < \
                math.hypot(*espeed) * 2:
            self.parent.speed[0] += espeed[0]
            self.parent.speed[1] += espeed[1]

    def get_exit_angle(self, obj_angle):
        circ_angle = self.parent.get_angle()
        return obj_angle - circ_angle + obj_angle

    def new_direction(self, radius, *angle):
        self.set_speed_after_angle(*angle)
        radius_diff = (self.parent.radius - radius)
        angle = self.parent.get_angle()
        self.parent.pos[0] += radius_diff * math.cos(angle)
        self.parent.pos[1] += radius_diff * math.sin(angle)

        self.status = 1

    def thrust(self, direction):
        if direction == 'up' and self.status < 3:
            self.parent.speed[1] += 300 / self.world.current_fps
            self.status += 1
        elif direction == 'down':
            self.parent.speed[1] -= 300 / self.world.current_fps
        elif direction == 'left':
            self.parent.speed[0] -= 75 / self.world.current_fps
        elif direction == 'right':
            self.parent.speed[0] += 75 / self.world.current_fps

    def update(self):
        self.parent.speed[1] -= 25.0 / self.world.current_fps
        speed_len = self.parent.get_speed()
        # Avoid the tunnelling effect by never travelling a distance
        # longer than the 20 pixels in one turn. This may seem
        # extreme, but the higher it is, the larger is the risk of the
        # solid passing through an object.
        pre_times = speed_len / 20
        times = int(math.ceil(pre_times))

        t = 1.0 / times
        for i in range(times):
            if i == times - 1:
                t = math.fmod(pre_times, 1) * t
            self.parent.pos[0] += self.parent.speed[0] * t
            self.parent.pos[1] += self.parent.speed[1] * t
            cols = []
            for x in self.level.objects:
                args = x.check_for_collision(self.parent)
                if args and x.bounce_off:
                    cols.append(args)
            if len(cols) > 1:
                radius = min([x[1] for x in cols])
                self.new_direction(radius, *[x[0] for x in cols])
            elif cols:
                self.new_direction(cols[0][1], cols[0][0])
