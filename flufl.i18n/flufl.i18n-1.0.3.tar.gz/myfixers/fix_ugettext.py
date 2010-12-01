# Copyright (C) 2009, 2010 by Barry A. Warsaw
#
# This file is part of flufl.i18n
#
# flufl.i18n is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, version 3 of the License.
#
# flufl.i18n is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License
# for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with flufl.i18n.  If not, see <http://www.gnu.org/licenses/>.

"""Additional 2to3 fixers."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'FixUgettext'
    ]


from lib2to3.fixer_base import BaseFix
from lib2to3.fixer_util import Name


class FixUgettext(BaseFix):
    """.ugettext -> .gettext"""

    PATTERN = """
    power< before=any+ trailer< '.' name='ugettext' > any* >
    """

    def transform(self, node, results):
        """See `BaseFix.transform()`"""
        name = results['name']
        name.replace(Name('gettext', prefix=name.prefix))
