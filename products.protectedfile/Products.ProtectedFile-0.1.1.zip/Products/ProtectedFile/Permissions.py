from Products.CMFCore.permissions import AddPortalContent
try:
    from Products.CMFCore.permissions import AddPortalContent
except ImportError:
    from Products.CMFCore.CMFCorePermissions import AddPortalContent
ADD_CONTENT_PERMISSION = AddPortalContent