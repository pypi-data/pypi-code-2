# -*- coding: utf-8 -*-

import sys
import logging

from AccessControl import ModuleSecurityInfo
from zope.i18nmessageid import MessageFactory

from Products.CMFCore import utils
from Products.Archetypes.public import process_types, listTypes

from Products.SimpleAlias import content
from Products.SimpleAlias.config import PROJECTNAME
from Products.SimpleAlias import Permissions

logger = logging.getLogger(PROJECTNAME)

# Module aliases - we don't always get it right on the first try, but and we
# can't move modules around because things are stored in the ZODB with the
# full module path. However, we can create aliases for backwards compatability.
sys.modules['Products.SimpleAlias.Alias'] = content.alias

SimpleAliasMessageFactory = MessageFactory('simplealias')
ModuleSecurityInfo('Products.SimpleAlias').declarePublic('SimpleAliasMessageFactory')

def initialize(context):
    import Products.SimpleAlias.content.alias

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = Permissions.ADD_ALIAS_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)

    from Products.SimpleAlias.SimpleAliasTool import SimpleAliasTool
    utils.ToolInit(
        'SimpleAlias tool',
        tools=(SimpleAliasTool,),
        icon='tool.gif', ).initialize(context)

