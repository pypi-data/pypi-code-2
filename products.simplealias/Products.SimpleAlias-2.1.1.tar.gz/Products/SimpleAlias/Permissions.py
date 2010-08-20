from AccessControl import ModuleSecurityInfo
security = ModuleSecurityInfo("Products.SimpleAlias.Permissions")

from Products.CMFCore.permissions import setDefaultRoles

security.declarePublic("ADD_ALIAS_PERMISSION")
ADD_ALIAS_PERMISSION='SimpleAlias: Add Alias'
setDefaultRoles(ADD_ALIAS_PERMISSION, ('Contributor', 'Manager', 'Owner'))

