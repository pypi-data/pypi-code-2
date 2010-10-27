from Products.CMFCore.permissions import setDefaultRoles
from Products.Archetypes.public import listTypes
from Products.SimpleBlog.config import PROJECTNAME

# Add Entry
CROSS_POST_PERMISSION='SimpleBlog: Cross-post'
VIEW_PORTLET_PERMISSION="SimpleBlog: View portlet"

setDefaultRoles(CROSS_POST_PERMISSION, ( 'Manager', 'Owner' ) )
setDefaultRoles(VIEW_PORTLET_PERMISSION, ('Anonymous',  )) 

TYPE_ROLES = ('Manager', 'Owner')

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    global permissions
    blog_types = listTypes(PROJECTNAME)
    for btype in blog_types:
        permission = "%s: Add %s" % (PROJECTNAME, btype['portal_type'])
        setDefaultRoles(permission, TYPE_ROLES)
        
        permissions[btype['portal_type']] = permission
    return permissions