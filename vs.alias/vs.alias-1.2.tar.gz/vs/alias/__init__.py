# $Id: __init__.py 9 2009-05-02 16:10:58Z veit $

from zope.i18nmessageid import MessageFactory
from config import PROJECTNAME

from Products.CMFCore import utils 
from Products.Archetypes import atapi
from vs.alias import config

AliasMessageFactory = MessageFactory(config.I18NDOMAIN)

def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    ADD_PERMISSIONS={} 
    for type in content_types:
        ADD_PERMISSIONS[type.portal_type] = """Add %s""" %type.portal_type

    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
        content_types      = (atype,),
        permission         = ADD_PERMISSIONS[atype.portal_type],
        extra_constructors = (constructor,),
        ).initialize(context) 

