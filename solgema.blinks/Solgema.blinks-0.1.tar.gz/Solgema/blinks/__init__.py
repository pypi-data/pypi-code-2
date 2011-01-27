from Products.CMFCore import DirectoryView

GLOBALS = globals()

DirectoryView.registerDirectory('skins', GLOBALS)

from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "Solgema.blinks"
DEFAULT_ADD_CONTENT_PERMISSION = "%s: Manage portlet" % PROJECTNAME

setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager',))

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    # Initialize content types
