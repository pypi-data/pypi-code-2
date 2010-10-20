"""Main product initializer
"""

from zope.i18nmessageid import MessageFactory
from Products.FileExchange import config

from Products.Archetypes import atapi
from Products.CMFCore import utils as cmfutils

FileExchangeMessageFactory = MessageFactory('FileExchange')

def initialize(context):

    from content import fileexchangecontainer, fileexchangefile

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    for atype, constructor in zip(content_types, constructors):
        cmfutils.ContentInit("%s: %s" % (config.PROJECTNAME, atype.portal_type),
            content_types      = (atype,),
            permission         = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor,),
            ).initialize(context)

