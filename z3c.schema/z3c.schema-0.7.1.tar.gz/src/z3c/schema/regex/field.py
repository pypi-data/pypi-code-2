##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""
$Id: field.py 91149 2008-09-14 22:39:34Z rogerineichen $
"""
__docformat__ = "reStructuredText"

import re
import zope.interface
import zope.schema

from z3c.schema.regex import interfaces


class Regex(zope.schema.ASCIILine):
    """Regex schema field.

    Must be a compilable regular expression
    """

    zope.interface.implements(interfaces.IRegex)

    def _validate(self, value):
        super(Regex, self)._validate(value)
        try:
            re.compile(value)
        except re.error, e:
            raise interfaces.InvalidRegex, '%r, %s' % (value, e)

    def fromUnicode(self, value):
        v = str(value.strip())
        self.validate(v)
        return v
