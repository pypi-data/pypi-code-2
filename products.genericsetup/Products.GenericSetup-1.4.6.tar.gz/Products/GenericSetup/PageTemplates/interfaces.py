##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PageTemplate interfaces.

$Id: interfaces.py 110540 2010-04-06 03:18:52Z tseaver $
"""

from zope.interface import Interface


class IZopePageTemplate(Interface):

    """Page Templates using TAL, TALES, and METAL.
    """

    def read():
        """Generate a text representation of the Template source.
        """

    def write(text):
        """Change the Template by parsing a read()-style source text.
        """
