from zope.i18nmessageid import MessageFactory
from Products.CMFCore.utils import ContentInit
from Products.Archetypes import process_types
from Products.Archetypes.public import listTypes
from Products.CMFPlone.utils import ToolInit

ShortUrlMessageFactory = MessageFactory('c2.app.shorturl')

from c2.app.shorturl.config import *


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    # Initialize portal content
    contentTypes, constructors, ftis = \
                process_types(listTypes(PROJECTNAME), PROJECTNAME)
    for i in range(0, len(contentTypes)):
        permission = "%s: Add %s" % (PROJECTNAME, ftis[i]['meta_type'])
        ContentInit("%s: %s" % (PROJECTNAME, ftis[i]['meta_type']),
                content_types=contentTypes,
                permission=permission,
                extra_constructors=constructors,
                ).initialize(context)
