# -*- coding: utf-8 -*-

# Helm
# config.py

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

from helm.models.cpu import CPU
from helm.models.mem import Mem, Swap
from helm.models.fs import FS
from helm.views.bar import Bar
from helm.views.histogram import Histogram
from helm.views.ring import Ring
from helm.widgets.cpus import CPUs

from helm.helm import run


if __name__ == '__main__':
    run(60,
        Ring(CPU()),
        CPUs(Histogram),
        Bar(Mem()),
        Bar(Swap()),
        Bar(FS('/')))
