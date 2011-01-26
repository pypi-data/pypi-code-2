
from zope.interface import Interface
from zope.configuration.fields import MessageID
from zope.configuration.fields import GlobalObject


class IRegisterPipelineElement(Interface):
    """unicodelexicon:registerPipelineElement directive"""

    group = MessageID(
        title=u'Group',
        description=u'Element group',
        required=True)

    name = MessageID(
        title=u'Name',
        description=u'Element name',
        required=True)

    factory = GlobalObject(
        title=u'Factory',
        description=u'Element factory',
        default=None,
        required=False)


def registerPipelineElement(_context, group, name, factory=None):
    from Products.UnicodeLexicon.pipelinefactory import element_factory
    _context.action(
        discriminator=('registerPipelineElement', group, name),
        callable=element_factory.registerFactory,
        args=(group, name, factory),
        )

