import zope.security.interfaces
import zope.component

from Products.Archetypes import atapi
from Products.CMFCore import utils


class Registration(object):
    def __init__(self, product, class_, permission_id):
        self.product = product
        self.class_ = class_
        self.permission_id = permission_id

    def __call__(self, context):
        # Load type information
        content_types, constructors, ftis = atapi.process_types(
            atapi.listTypes(self.product), self.product
            )

        # Loop through all content types for this product
        for atype, constructor in zip(content_types, constructors):
            # Bad API impedance!
            if not atype is self.class_:
                continue

            # Look up Zope 3 permission component
            permission = zope.component.getUtility(
                zope.security.interfaces.IPermission,
                self.permission_id
                )

            # Set default roles to register permission
            #setDefaultRoles(permission.title, ())

            utils.ContentInit('%s: %s' % (self.product, atype.portal_type),
                content_types=(atype, ),
                permission=permission.title,
                extra_constructors=(constructor,),
                ).initialize(context)
