#!/usr/bin/env python

# Copyright (C) 2008, 2009  Andrey Golovizin
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Generate a bidirectional map between file formats and extensions."""

# XXX should it be in pybtex.plugins?

from os.path import basename
from glob import glob1
from pybtex.plugin import find_plugin

def available_formats():
    for filename in glob1('input', '*.py'):
        if filename != '__init__.py':
            yield filename.replace('.py', '')


def filetypes():
    for format in available_formats():
        plugin = find_plugin('pybtex.database.input', format)
        yield format, plugin.file_extension

def gen_formats():
    extension_for_format = dict(filetypes())
    format_for_extension = dict((value, key)
            for (key, value) in extension_for_format.iteritems())

    output = open('formats.py', 'w')
    output.write('# generated by %s\n' % basename(__file__))
    output.write('# do not edit\n\n')
    output.write('format_for_extension = %r\n\n' % format_for_extension)
    output.write('extension_for_format = %r\n' % extension_for_format)
    output.close()

if __name__ == '__main__':
    gen_formats()
