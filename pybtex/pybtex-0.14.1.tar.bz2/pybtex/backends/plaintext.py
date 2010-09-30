# Copyright (C) 2006, 2007, 2008, 2009  Andrey Golovizin
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

from pybtex.backends import BackendBase

file_extension = 'txt'

class Writer(BackendBase):
    symbols = {
        'ndash': u'-',
        'newblock': u' ',
        'nbsp': u' '
    }
    
    def format_tag(self, tag_name, text):
        return text
    
    def write_entry(self, key, label, text):
        self.output(u"[%s] " % label)
        self.output(text)
        self.output(u'\n')
