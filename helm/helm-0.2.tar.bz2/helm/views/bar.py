# -*- coding: utf-8 -*-

# Helm
# views/bar.py

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
from ..primitives import draw_line, draw_ring, draw_text, NORTHEAST
from .. import view


class Bar(view.View):
    def __init__(self, model):
        view.View.__init__(self)
        self.model = model

    def init(self, width, height=None):
        view.View.init(self, width, 20)

    def update(self):
        self.model.update()

    def draw(self, cr, width, height):
        pct = self.model.pct
        draw_line(cr, 0, 3, pct * self.width, 3, 6)

        draw_text(cr, 0, 6, self.model.name,
                  fg_color=(0, 1, 0, 1), bg_color=BLACK,
                  border=1)
        draw_text(cr, self.width - 1, 6, self.model.value,
                  fg_color=(0, 1, 0, 1), bg_color=BLACK,
                  border=1, reference=NORTHEAST)
