from Products.CMFCore import utils, DirectoryView
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
from Products.PFGSelectionStringField.config import *

# Register skin directories so they can be added to portal_skins
DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/PFGSelectionStringField', product_globals)

from zope.i18nmessageid import MessageFactory
PFGSelectionStringFieldMessageFactory = MessageFactory(PROJECTNAME)

def initialize(context):

    # Import the type, which results in registerType() being called
    from content import PFGSelectionStringField

    # initialize the content, including types and add permissions
    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    utils.ContentInit(
        PROJECTNAME + ' Content',
        content_types      = content_types,
        permission         = DEFAULT_ADD_CONTENT_PERMISSION,
        extra_constructors = constructors,
        fti                = ftis,
        ).initialize(context)
