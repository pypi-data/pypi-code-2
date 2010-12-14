# Copyright (C) 2003 gocept gmbh & co.kg
# Christian Zagrodnick, cz@gocept.com
# $Id: helpers.py 31512 2010-12-14 10:13:34Z mac $
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
#

import re


_string_parser_pattern = re.compile(r'^"?(.*?)"?$')
def parseString(s):
    passed = s
    if isinstance(s, list):
        if len(s) == 1 and isinstance(s[0], (str, unicode)):
            s = s[0]
    assert isinstance(s, (str, unicode)), "%r is not str or unicode (%r)" % (
        s, passed)
    m = _string_parser_pattern.match(s)
    if m is None:
        return ''
    return m.group(1).strip()
            


