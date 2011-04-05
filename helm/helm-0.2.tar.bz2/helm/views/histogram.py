# -*- coding: utf-8 -*-

# Helm
# views/histogram.py

# Copyright (C) 2011 Anaël Verrier <elghinn@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 only.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from ..color import BLACK, WHITE
from ..primitives import draw_line, draw_text, CENTER
from .. import view


class Histogram(view.View):
    def __init__(self, model):
        view.View.__init__(self)
        self.model = model
        self.values = None
        self.graph_height = 0
        self.text_height = 0

    def init(self, width, height=None):
        self.graph_height = 50
        self.text_height = 15
        view.View.init(self, width, self.graph_height + self.text_height)
        self.values = [0] * width

    def update(self):
        self.model.update()
        self.values.pop(0)
        self.values.append(self.model.pct)

    def draw(self, cr, width, height):
        for i in xrange(0, 5):
            draw_line(cr,
                      0, i * self.graph_height / 5 + .5,
                      self.width + 1, i * self.graph_height / 5 + .5, 1,
                      (0.56, 0.56, 0.56, 1.))

        for i, value in enumerate(self.values):
            draw_line(cr,
                      i + .5, self.graph_height,
                      i + .5, int((1 - value) * self.graph_height), 1)

        draw_text(cr, self.width / 2, self.graph_height + self.text_height / 2,
                  self.model.name,
                  fg_color=(0, 1, 0, 1), bg_color=BLACK,
                  border=1, reference=CENTER)
