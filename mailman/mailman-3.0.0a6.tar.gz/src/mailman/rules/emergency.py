# Copyright (C) 2007-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

"""The emergency hold rule."""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'Emergency',
    ]


from zope.interface import implements

from mailman.core.i18n import _
from mailman.interfaces.rules import IRule



class Emergency:
    """The emergency hold rule."""
    implements(IRule)

    name = 'emergency'

    description = _(
        """The mailing list is in emergency hold and this message was not
        pre-approved by the list administrator.
        """)

    record = True

    def check(self, mlist, msg, msgdata):
        """See `IRule`."""
        return mlist.emergency and not msgdata.get('moderator_approved')
