import Products
from AccessControl.Permission import _registeredPermissions
from AccessControl.Permission import pname
from AccessControl.Permission import ApplicationDefaultPermissions

# This is borrowed from Products.CMFCore to avoid a dependency.


def setDefaultRoles(permission, roles):
    registered = _registeredPermissions
    if permission not in registered:
        registered[permission] = 1
        Products.__ac_permissions__ = (
            Products.__ac_permissions__ + ((permission, (), roles),))
        mangled = pname(permission)
        setattr(ApplicationDefaultPermissions, mangled, roles)


def create_permission(permission, event):
    """When a new IPermission utility is registered (via the <permission />
    directive), create the equivalent Zope2 style permission.
    """
    setDefaultRoles(permission.title, ('Manager',))
