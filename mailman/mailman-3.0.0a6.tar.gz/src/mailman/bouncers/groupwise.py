# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
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

"""This appears to be the format for Novell GroupWise and NTMail

X-Mailer: Novell GroupWise Internet Agent 5.5.3.1
X-Mailer: NTMail v4.30.0012
X-Mailer: Internet Mail Service (5.5.2653.19)
"""

from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'GroupWise',
    ]


import re

from email.Message import Message
from cStringIO import StringIO
from zope.interface import implements

from mailman.interfaces.bounce import IBounceDetector


acre = re.compile(r'<(?P<addr>[^>]*)>')



def find_textplain(msg):
    if msg.get_content_type() == 'text/plain':
        return msg
    if msg.is_multipart:
        for part in msg.get_payload():
            if not isinstance(part, Message):
                continue
            ret = find_textplain(part)
            if ret:
                return ret
    return None



class GroupWise:
    """Parse Novell GroupWise and NTMail bounces."""

    implements(IBounceDetector)

    def process(self, msg):
        """See `IBounceDetector`."""
        if msg.get_content_type() != 'multipart/mixed' or not msg['x-mailer']:
            return None
        addresses = set()
        # Find the first text/plain part in the message.
        text_plain = find_textplain(msg)
        if text_plain is None:
            return None
        body = StringIO(text_plain.get_payload())
        for line in body:
            mo = acre.search(line)
            if mo:
                addresses.add(mo.group('addr'))
            elif '@' in line:
                i = line.find(' ')
                if i == 0:
                    continue
                if i < 0:
                    addresses.add(line)
                else:
                    addresses.add(line[:i])
        return list(addresses)
