from zope.i18nmessageid import MessageFactory

RichImageMessageFactory = MessageFactory('Products.RichImage')


def initialize(context):
    """Initializer called when used as a Zope 2 product.
    """
    try:
        from Products.LinguaPlone import public as atapi
        atapi # pyflakes
    except ImportError:
        from Products.Archetypes import atapi

    import Products.RichImage.content
    from Products.RichImage import config

    content_types, constructors, ftis = atapi.process_types(
        atapi.listTypes(config.PROJECTNAME),
        config.PROJECTNAME)

    from Products.CMFCore import utils
    for atype, constructor in zip(content_types, constructors):
        utils.ContentInit('%s: %s' % (config.PROJECTNAME, atype.portal_type),
            content_types = (atype, ),
            permission = config.ADD_PERMISSIONS[atype.portal_type],
            extra_constructors = (constructor, ),
            ).initialize(context)
