from Products.CMFCore import utils#, DirectoryView
from Products.Archetypes.public import (
    process_types,
)
from Products.Archetypes import listTypes
from Products.PFGExtendedMailAdapter.config import (
    DEFAULT_ADD_CONTENT_PERMISSION,
    PROJECTNAME,
)

from zope.i18nmessageid import MessageFactory
PFGExtendedMailAdapterMessageFactory = MessageFactory(PROJECTNAME)

def initialize(context):

    # Import the type, which results in registerType() being called
    from content import PFGExtendedMailAdapter

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
