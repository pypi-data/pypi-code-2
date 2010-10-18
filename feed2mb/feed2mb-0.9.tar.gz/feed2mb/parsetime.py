# -*- coding: utf-8 -*-
# feed2mb
# Copyright (C) 2008 EBC - Empresa Brasil de Comunicação
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from datetime import timedelta

retime = re.compile('([0-9]{2}):([0-5][0-9])')

def parsetime(stime):
    try:
        se= retime.match(stime)
        matches = se.groups()
        delta = timedelta(hours = int(matches[0]), minutes = int(matches[1]))
        return delta.days * 24 *60 *60 + delta.seconds
    except:
        raise Exception, 'String format error'
