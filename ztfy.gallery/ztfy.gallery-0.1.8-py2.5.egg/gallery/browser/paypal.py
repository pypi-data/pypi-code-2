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
from z3c.json.interfaces import IJSONWriter
from zope.traversing.interfaces import TraversalError

# import local interfaces
from ztfy.blog.interfaces.site import ISiteManager
from ztfy.blog.layer import IZTFYBlogBackLayer
from ztfy.gallery.interfaces import IGalleryManagerPaypalInfo, IGalleryImage, IGalleryImagePaypalInfo, \
                                    IGalleryImageExtension

# import Zope3 packages
from z3c.form import field, button
from z3c.formjs import ajax, jsaction
from z3c.template.template import getLayoutTemplate
from zope.app import zapi
from zope.component import adapts
from zope.event import notify
from zope.interface import implements
from zope.lifecycleevent import ObjectModifiedEvent
from zope.publisher.browser import BrowserPage
from zope.traversing import namespace

# import local packages
from ztfy.blog.browser.skin import IDialogEditFormButtons, BaseDialogSimpleEditForm
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
        raise TraversalError('++paypal++')


class SiteManagerPaypalMenuItem(JsMenuItem):
    """Paypal properties menu item"""

    title = _(":: Paypal account...")


class SiteManagerPaypalEditForm(BaseDialogSimpleEditForm):
    """Site manager Paypal edit form"""

    legend = _("Edit Paypal properties")

    fields = field.Fields(IGalleryManagerPaypalInfo)
    layout = getLayoutTemplate()
    parent_interface = ISiteManager
    parent_view = SiteManagerEditForm

    def getContent(self):
        return IGalleryManagerPaypalInfo(self.context)


class GalleryImagePaypalNamespaceTraverser(namespace.view):
    """++paypal++ namespace for images"""

    def traverse(self, name, ignored):
        result = IGalleryImagePaypalInfo(self.context, None)
        if result is not None:
            return result
        raise TraversalError('++paypal++')


class GalleryImagePaypalExtension(object):
    """Gallery image Paypal extension"""

    adapts(IGalleryImage, IZTFYBlogBackLayer)
    implements(IGalleryImageExtension)

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.paypal = IGalleryImagePaypalInfo(self.context)

    title = _("Enable or disable Paypal")

    @property
    def icon(self):
        if self.paypal.paypal_enabled:
            name = "enabled"
        else:
            name = "disabled"
        return '/++skin++Gallery/@@/ztfy.gallery.back.img/paypal-%s.png' % name

    @property
    def klass(self):
        if self.paypal.paypal_enabled:
            return 'paypal enabled'
        else:
            return 'paypal disabled'

    @property
    def url(self):
        return """javascript:$.ZBlog.gallery.paypal_switch('%s');""" % zapi.getName(self.context)

    weight = 50


class GalleryImagePaypalEditForm(BaseDialogSimpleEditForm):
    """Gallery image Paypal edit form"""

    buttons = button.Buttons(IDialogEditFormButtons)
    fields = field.Fields(IGalleryImagePaypalInfo)

    def __call__(self):
        info = IGalleryImagePaypalInfo(self.context)
        if info.paypal_enabled:
            return super(GalleryImagePaypalEditForm, self).__call__()
        else:
            info.paypal_enabled = True
            writer = zapi.getUtility(IJSONWriter)
            return writer.write({ 'output': u'OK' })

    @jsaction.handler(buttons['dialog_submit'])
    def submit_handler(self, event, selector):
        return '''$.ZBlog.gallery.paypal_edit(this.form);'''

    @jsaction.handler(buttons['dialog_cancel'])
    def cancel_handler(self, event, selector):
        return '$.ZBlog.dialog.close();'

    @ajax.handler
    def ajaxEdit(self):
        writer = zapi.getUtility(IJSONWriter)
        self.updateWidgets()
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            self.update()
            return writer.write({ 'output': self.layout() })
        if self.applyChanges(data):
            parent = getParent(self.context, self.parent_interface)
            notify(ObjectModifiedEvent(parent))
            return writer.write({ 'output': u'OK',
                                  'enabled': IGalleryImagePaypalInfo(self.context).paypal_enabled })
        else:
            return writer.write({ 'output': u'NONE' })
