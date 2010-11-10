"""Common configuration constants
"""
from AccessControl import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'raptus.article.flash'

security = ModuleSecurityInfo('raptus.article.flash.config')

security.declarePublic('ADD_PERMISSION')
ADD_PERMISSION = 'raptus.article: Add Flash'
setDefaultRoles(ADD_PERMISSION, ('Manager','Contributor',))
