from Products.CMFCore.permissions import setDefaultRoles

PROJECTNAME = 'Products.RichImage'

ADD_PERMISSIONS = {
    'RichImage': 'Products.RichImage: Add RichImage',
}

for p in ADD_PERMISSIONS.values():
    setDefaultRoles(p, ('Owner', 'Manager'))
