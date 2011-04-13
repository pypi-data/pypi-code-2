#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Helm
# helm_launcher.py

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

from os import execl

from xdg import BaseDirectory as basedir


def main():
    config_file = basedir.load_first_config('helm', 'config.py')
    if config_file is None:
        config_file = 'config.py'

    execl('/usr/bin/env', 'env', 'python', config_file)


if __name__ == '__main__':
    main()
