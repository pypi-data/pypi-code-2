from Products.CMFCore.permissions import setDefaultRoles
PROJECTNAME = "PFGVerkkomaksut"

setDefaultRoles("Add PFGVerkkomaksut", ('Manager',))

ADD_PERMISSIONS = {
    "PFGVerkkomaksut" : "Add PFGVerkkomaksut",
}
