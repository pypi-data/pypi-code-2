

import Globals
try:
    # Zope 2.12
    from App.Common import package_home
except ImportError:
    from Globals import package_home

from Products.CMFCore.DirectoryView import registerDirectory
from Products.CMFCore.utils import ContentInit
try:
    from Products.CMFCore.permissions import View, AddPortalContent
except ImportError: # For instances with old CMF products
    from Products.CMFCore.CMFCorePermissions import View, AddPortalContent

try:
    from Products.Archetypes.atapi import process_types, listTypes
except ImportError:
    from Products.Archetypes.public import process_types, listTypes

from config import *

from AccessControl import allow_module

global fckeditor_globals
fckeditor_globals=globals()

if INSTALL_DEMO_TYPES :
    import RichContentDemo



registerDirectory(SKINS_DIR, GLOBALS)


def initializeTypes(context):
    type_list = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(type_list, PROJECTNAME)
    all_types = zip(content_types, constructors)
    for atype, constructor in all_types:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = AddPortalContent,
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)

def initialize(context):
    allow_module('Products.FCKeditor.utils')
    if INSTALL_DEMO_TYPES :
        initializeTypes(context)







