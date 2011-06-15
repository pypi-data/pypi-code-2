
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.DirectoryView import registerDirectory

from Products.Archetypes.public import *
from Products.Archetypes import listTypes

from Products.ProtectedFile.config import SKINS_DIR, GLOBALS, PROJECTNAME
from Products.ProtectedFile.config import ADD_CONTENT_PERMISSION

registerDirectory(SKINS_DIR, GLOBALS)


def initialize(context):

    # process our custom types
    from Products.ProtectedFile import types
    
    content_types, constructors, ftis = process_types(listTypes(PROJECTNAME), PROJECTNAME)

    ContentInit(
        PROJECTNAME + ' Content',
        content_types = content_types,
        permission = ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti = ftis,
        ).initialize(context)

