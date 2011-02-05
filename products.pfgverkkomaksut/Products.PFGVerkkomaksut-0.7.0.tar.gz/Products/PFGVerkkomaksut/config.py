# BBB for CMF 1.4
try:
    from Products.CMFCore.permissions import setDefaultRoles
except ImportError:
    from Products.CMFCore.CMFCorePermissions import setDefaultRoles

PROJECTNAME = "PFGVerkkomaksut"
DEFAULT_ADD_CONTENT_PERMISSION = "Add PFGVerkkomaksut"
product_globals=globals()

setDefaultRoles(DEFAULT_ADD_CONTENT_PERMISSION, ('Manager', 'Owner',))
