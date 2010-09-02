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
from persistent import Persistent

# import Zope3 interfaces
from zope.annotation.interfaces import IAnnotations

# import local interfaces
from interfaces import IGalleryManagerPaypalInfo
from ztfy.blog.interfaces.site import ISiteManager

# import Zope3 packages
from zope.app.container.contained import Contained
from zope.component import adapts
from zope.interface import implements
from zope.location import locate
from zope.proxy import ProxyBase, setProxiedObject
from zope.schema.fieldproperty import FieldProperty

# import local packages
from ztfy.i18n.property import I18nTextProperty, I18nImageProperty


class SiteManagerPaypalInfo(Persistent, Contained):

    implements(IGalleryManagerPaypalInfo)

    paypal_enabled = FieldProperty(IGalleryManagerPaypalInfo['paypal_enabled'])
    paypal_currency = FieldProperty(IGalleryManagerPaypalInfo['paypal_currency'])
    paypal_button_id = FieldProperty(IGalleryManagerPaypalInfo['paypal_button_id'])
    paypal_format_options = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_format_options'])
    paypal_options_label = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_options_label'])
    paypal_options_options = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_options_options'])
    paypal_image_field_name = FieldProperty(IGalleryManagerPaypalInfo['paypal_image_field_name'])
    paypal_image_field_label = I18nTextProperty(IGalleryManagerPaypalInfo['paypal_image_field_label'])
    add_to_basket_button = I18nImageProperty(IGalleryManagerPaypalInfo['add_to_basket_button'])
    see_basket_button = I18nImageProperty(IGalleryManagerPaypalInfo['see_basket_button'])
    paypal_pkcs_key = FieldProperty(IGalleryManagerPaypalInfo['paypal_pkcs_key'])


PAYPAL_ANNOTATIONS_KEY = 'ztfy.gallery.sitemanager.paypal'

class SiteManagerPaypalAdapter(ProxyBase):

    adapts(ISiteManager)
    implements(IGalleryManagerPaypalInfo)

    def __init__(self, context):
        annotations = IAnnotations(context)
        info = annotations.get(PAYPAL_ANNOTATIONS_KEY)
        if info is None:
            info = annotations[PAYPAL_ANNOTATIONS_KEY] = SiteManagerPaypalInfo()
            locate(info, context, '++paypal++')
        setProxiedObject(self, info)
