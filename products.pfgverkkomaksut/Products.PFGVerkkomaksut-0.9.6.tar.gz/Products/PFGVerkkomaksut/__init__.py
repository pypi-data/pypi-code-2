#from Globals import package_home
from Products.CMFCore import utils, DirectoryView
from Products.Archetypes.public import *
from Products.Archetypes import listTypes
#from Products.Archetypes.utils import capitalize

#import os, os.path, sys, content, widget


# Get configuration data, permissions
from Products.PFGVerkkomaksut.config import *

# Register skin directories so they can be added to portal_skins
DirectoryView.registerDirectory('skins', product_globals)
DirectoryView.registerDirectory('skins/PFGVerkkomaksut', product_globals)
#DirectoryView.registerDirectory('skins/attachment_widgets', product_globals)

from zope.i18nmessageid import MessageFactory
PFGVerkkomaksutMessageFactory = MessageFactory(PROJECTNAME)

def initialize(context):

    # Import the type, which results in registerType() being called
    from content import PFGVerkkomaksut

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
