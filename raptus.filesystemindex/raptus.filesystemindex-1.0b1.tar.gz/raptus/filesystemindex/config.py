"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.filesystemindex'

security = ModuleSecurityInfo('raptus.filesystemindex.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = 'raptus.filesystemindex: Add FileSystemIndex'
setDefaultRoles(ADD_PERMISSION, ('Manager','Contributor',))
