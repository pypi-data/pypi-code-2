# Copyright (C) 2003 gocept gmbh & co.kg, 06366 Koethen/Anahlt, Germany
# Christian Zagrodnick, cz@gocept.com
# $Id: tcmfile.py 31512 2010-12-14 10:13:34Z mac $
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


import re

class TCMFile:
    """parser for tcm files"""
    
    _line_pattern = re.compile(r"^\s*{\s*(\w+)\s+(.*)\s+}$")
    
    def __init__(self, f):
        self._file = f
        self._line = ''

    def parse(self):
        return self._parse_toplevel()

    def _next_line(self):
        """
        post:
            isinstance(self._line, str)
        """
        line = self._file.readline()
        if line == '':
            line = None
        else:
            line = line.strip()
        self._line = line

    def data(self):
        return self._line

    def _parse_toplevel(self):
        parsed = {}
        while self.data() is not None:
            self._next_line()
            section = self.data()
            if not section:
                continue
            if section.startswith('#'):
                # comment
                continue
            section = section.split()
            assert len(section) in (1, 2), "The file seems invalid (got %r)" % (
                section, )
            if len(section) == 1:
                section_id = None
                section_name = section[0]
            else:
                section_id = section[1]
                section_name = section[0]
            section_data = self._parse_section(section_name, section_id)
            parsed.setdefault(section_name, []).append(section_data)
        return parsed
        
    def _parse_section(self, section_name, section_id):
        section = {}
        section['_id'] = section_id
        section['_name'] = section_name
        self._next_line()
        while self.data() != '}':
            line = self._parse_line()
            if line is None:
                continue
            key, value = line
            section.setdefault(key, []).append(value)
        return section
   
    def _parse_line(self):
        self._next_line()
        m = self._line_pattern.match(self.data())
        if m is None:
            return None
        key = m.group(1)
        value = m.group(2)
        return key, value

