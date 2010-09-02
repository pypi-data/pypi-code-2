### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2010 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces
from z3c.form import field
from z3c.template.template import getLayoutTemplate
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.gallery.interfaces import IGalleryManagerPaypalInfo

# import Zope3 packages
from zope.traversing import namespace

# import local packages
from ztfy.blog.browser.skin import BaseDialogSimpleEditForm
from ztfy.blog.browser.site import SiteManagerEditForm
from ztfy.skin.menu import JsMenuItem
from ztfy.utils.traversing import getParent

from ztfy.gallery import _


class SiteManagerPaypalNamespaceTraverser(namespace.view):
    """++paypal++ namespace"""

    def traverse(self, name, ignored):
        result = getParent(self.context, ISiteManager)
        if result is not None:
            return IGalleryManagerPaypalInfo(result)
        raise TraversalError('++gallery++')


class SiteManagerPaypalMenuItem(JsMenuItem):
    """Paypal properties menu item"""

    title = _(":: Paypal properties...")


class SiteManagerPaypalEditForm(BaseDialogSimpleEditForm):
    """Site manager Paypal edit form"""

    legend = _("Edit Paypal properties")

    fields = field.Fields(IGalleryManagerPaypalInfo)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    parent_view = SiteManagerEditForm

    def getContent(self):
        return IGalleryManagerPaypalInfo(self.context)
