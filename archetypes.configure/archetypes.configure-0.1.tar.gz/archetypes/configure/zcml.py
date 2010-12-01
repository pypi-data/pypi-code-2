import Products
import Products.Archetypes.atapi

import zope.interface
import zope.schema
import zope.configuration.fields
import zope.i18nmessageid

from registry import Registration

_ = zope.i18nmessageid.MessageFactory('archetypes')

_add_permission = "cmf.AddPortalContent"


class IRegisterDirective(zope.interface.Interface):
    class_ = zope.configuration.fields.GlobalObject(
        title=_("Archetypes content class"),
        description=_("Python name of the implementation object.  This"
                      " must identify an object in a module using the"
                      " full dotted name."),
        required=True,
        )

    package = zope.configuration.fields.GlobalObject(
        title=_(u"Target package"),
        description=_(u"Defaults to the configuration context's package."),
        required=False,
        )

    product = zope.schema.TextLine(
        title=_("Product name"),
        description=_("Zope 2 product name. This defaults to the "
                      "configuration context's module name."),
        required=False,
        )

    permission = zope.security.zcml.Permission(
        title=_("Permission"),
        description=_("Permission required to add this content object."),
        required=False,
        )


def handler(product, package, class_, permission_id):
    Products.Archetypes.atapi.registerType(class_, product)
    registration = Registration(product, class_, permission_id)
    to_initialize = Products.__dict__.setdefault('_packages_to_initialize', [])
    to_initialize.append((package, registration))


def register(_context, class_, product=None,
             package=None, permission=_add_permission):
    if package is None:
        package = _context.package

    if product is None:
        product = package.__name__

    _context.action(
        discriminator=('register', class_),
        callable=handler,
        args=(product, package, class_, permission),
        )
