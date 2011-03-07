"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = "raptus.showcase"

ADD_PERMISSIONS = {
    "Showcase": "Showcase: Add Showcase",
    "ShowcaseImage": "Showcase: Add ShowcaseImage",
}

security = ModuleSecurityInfo('raptus.showcase.config')

security.declarePublic('AddShowcase')
setDefaultRoles(ADD_PERMISSIONS['Showcase'], ('Manager','Contributer','Owner',))

security.declarePublic('AddShowcaseImage')
setDefaultRoles(ADD_PERMISSIONS['ShowcaseImage'], ('Manager','Contributer','Owner',))

product_globals = globals()