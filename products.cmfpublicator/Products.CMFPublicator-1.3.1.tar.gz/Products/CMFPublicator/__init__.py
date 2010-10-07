# -*- coding: utf-8 -*-

from zope.i18nmessageid import MessageFactory as BaseMessageFactory
MessageFactory = BaseMessageFactory('Products.CMFPublicator')

from Products.CMFPublicator import config
from Products.CMFPublicator import PublicatorTool

from Products.Archetypes import atapi
from Products.CMFCore import utils

from Products.CMFPlone.utils import ToolInit

# Define a message factory for when this product is internationalised.
# This will be imported with the special name "_" in most modules. Strings
# like _(u"message") will then be extracted by i18n tools for translation.

def initialize(context):
    """Initializer called when used as a Zope 2 product.

    This is referenced from configure.zcml. Registrations as a "Zope 2 product"
    is necessary for GenericSetup profiles to work, for example.

    Here, we call the Archetypes machinery to register our content types
    with Zope and the CMF.
    """


    tools = [PublicatorTool.PublicatorTool]
    ToolInit(config.PROJECTNAME +' Tools',
                tools = tools,
                ).initialize( context )