# Copyright (c) 2010 by Lorenzo Gil Sanchez <lorenzo.gil.sanchez@gmail.com>
#
# This file is part of hghooks.
#
# hghooks is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# hghooks is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with hghooks.  If not, see <http://www.gnu.org/licenses/>.

import re

version = "0.1.2"

re_options = re.IGNORECASE | re.MULTILINE | re.DOTALL
skip_pattern = re.compile('# hghooks: (.*)', re_options)


def skip_file(filename, skip_text):
    if not filename.endswith('.py'):
        return True

    matches = skip_pattern.findall(open(filename, 'r').read())
    for match in matches:
        if skip_text in match:
            return True

    return False
