# -*- coding: utf-8 -*-

# Helm
# color.py

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

class Color(list):
    def __init__(self, rgb=0x000000, alpha=1):
        self.append(((rgb / 0x10000) % 0x100) / 255)
        self.append(((rgb / 0x100) % 0x100) / 255)
        self.append((rgb % 0x100) / 255)
        self.append(alpha)

BLACK = Color()
WHITE = Color(0xffffff)
