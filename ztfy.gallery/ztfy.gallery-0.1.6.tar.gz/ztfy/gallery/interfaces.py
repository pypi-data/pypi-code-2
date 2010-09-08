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
from zope.app.container.interfaces import IContained

# import local interfaces
from ztfy.blog.interfaces.container import IOrderedContainer
from ztfy.blog.interfaces.paragraph import IParagraphInfo, IParagraphWriter, IParagraph
from ztfy.i18n.interfaces import II18nAttributesAware

# import Zope3 packages
from zope.app.container.constraints import contains, containers
from zope.interface import Interface
from zope.schema import Int, Bool, Text, TextLine, URI, Choice

# import local packages
from ztfy.file.schema import ImageField
from ztfy.i18n.schema import I18nText, I18nTextLine, I18nImage

from ztfy.gallery import _


class IGalleryNamespaceTarget(Interface):
    """Marker interface for targets handling '++gallery++' namespace traverser"""


class IGalleryImageInfo(II18nAttributesAware):
    """Gallery image base interface"""

    title = I18nTextLine(title=_("Title"),
                         description=_("Image's title"),
                         required=False)

    description = I18nText(title=_("Description"),
                           description=_("Short description of the image"),
                           required=False)

    credit = TextLine(title=_("Author credit"),
                      description=_("Credit and copyright notices of the image"),
                      required=False)

    image = ImageField(title=_("Image data"),
                       description=_("Current content of the image"),
                       required=True)

    image_id = TextLine(title=_("Image ID"),
                        description=_("Unique identifier of this image in the whole collection"),
                        required=False)

    visible = Bool(title=_("Visible image ?"),
                   description=_("Select 'No' to hide this image"),
                   required=True,
                   default=True)

    def title_or_id():
        """Get image's title or ID"""


class IGalleryImage(IGalleryImageInfo, IContained):
    """Gallery image full interface"""

    containers('ztfy.gallery.interfaces.IGalleryContainer')


class IGalleryImageExtension(Interface):
    """Gallery image extension info"""

    title = TextLine(title=_("Extension title"),
                     required=True)

    url = TextLine(title=_("Extension view URL"),
                   required=True)

    icon = URI(title=_("Extension icon URL"),
               required=True)

    weight = Int(title=_("Extension weight"),
                 required=True,
                 default=50)


class IGalleryContainerInfo(Interface):
    """Gallery container base interface"""

    def getVisibleImages():
        """Get visible images in ordered list"""


class IGalleryContainer(IGalleryContainerInfo, IOrderedContainer, IGalleryNamespaceTarget):
    """Gallery images container interface"""

    contains(IGalleryImage)


class IGalleryContainerTarget(IGalleryNamespaceTarget):
    """Marker interface for gallery images container target"""


class IGalleryManagerPaypalInfo(II18nAttributesAware):
    """Global Paypal informations for site manager"""

    paypal_enabled = Bool(title=_("Enable Paypal payments"),
                          description=_("Enable or disable Paypal payments globally"),
                          required=True,
                          default=False)

    paypal_currency = TextLine(title=_("Paypal currency"),
                               description=_("Currency used for Paypal exchanges"),
                               required=False,
                               max_length=3,
                               default=u'EUR')

    paypal_button_id = TextLine(title=_("Paypal button ID"),
                                description=_("Internal number of Paypal registered payment button"),
                                required=False)

    paypal_format_options = I18nText(title=_("'Format' options"),
                                     description=_("Enter 'Format' options values ; values and labels may be separated by a '|'"),
                                     required=False)

    paypal_options_label = I18nTextLine(title=_("'Options' label"),
                                        description=_("Label applied to 'Options' selection box"),
                                        required=False)

    paypal_options_options = I18nText(title=_("'Options' options"),
                                      description=_("Enter 'Options' options values ; values and labels may be separated by '|'"),
                                      required=False)

    paypal_image_field_name = TextLine(title=_("Image ID field name"),
                                       description=_("Paypal ID of hidden field containing image ID"),
                                       required=False)

    paypal_image_field_label = I18nTextLine(title=_("Image ID field label"),
                                            description=_("Paypal label of field containing image ID"),
                                            required=False)

    add_to_basket_button = I18nImage(title=_("'Add to basket' image"),
                                     description=_("Image containing 'Add to basket' link"),
                                     required=False)

    see_basket_button = I18nImage(title=_("'See basket' image"),
                                  description=_("Image containing 'See basket' link"),
                                  required=False)

    paypal_pkcs_key = Text(title=_("Paypal basket PKCS key"),
                           description=_("Full PKCS key used to access Paypal basket"),
                           required=False)


#
# Gallery paragraphs management
#

class IGalleryParagraphRenderer(Interface):
    """Gallery paragraph renderer"""

    label = TextLine(title=_("Renderer name"),
                     required=True)

    def update():
        """Update gallery paragraph renderer"""

    def render():
        """Render gallery paragraph renderer"""


class IGalleryParagraphInfo(IParagraphInfo):
    """Gallery link paragraph base interface"""

    renderer = Choice(title=_("Paragraph renderer"),
                      description=_("Renderer used to render this gallery"),
                      required=True,
                      default=u'default',
                      vocabulary="ZTFY Gallery renderers")


class IGalleryParagraphWriter(IParagraphWriter):
    """Gallery link paragraph writer interface"""


class IGalleryParagraph(IParagraph, IGalleryParagraphInfo, IGalleryParagraphWriter):
    """Gallery link interface full interface"""
