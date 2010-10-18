##############################################################################
#
# Copyright (c) 2005 Zope Foundation and Contributors.
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
"""Adding that redirects to plugins.html.

$Id: adding.py 113109 2010-06-04 11:54:46Z janwijbrand $
"""

import zope.app.container.browser.adding

from zope.traversing.browser.absoluteurl import absoluteURL

class Adding(zope.app.container.browser.adding.Adding):

    def nextURL(self):
        return absoluteURL(self.context, self.request) + '/@@contents.html'
