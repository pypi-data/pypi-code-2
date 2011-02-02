from zope.interface import Interface, Attribute, implements

from zope.container.interfaces import IContainer as IContainerBase
from grokcore.component.interfaces import IContext

# FIXME: this doesn't depend on grok.interfaces.IContainer. If something
# is registered directly for those containers, it won't show up for
# this IContainer... Want to avoid directly having to depend on Grok
# with megrok.rdb however
class IContainer(IContext, IContainerBase):
    def set(value):
        """Add a new value to the container without having to specify the key.

        Lets the container figure out an appropriate key.


        Defined by SQLAlchemy dictionary-based collections.
        """

    def remove(value):
        """Remove a value from the container, by value.

        
        Defined by SQLAlchemy dictionary-based collections.
        """


class IDatabaseSetupEvent(Interface):
    metadata = Attribute("Metadata that was just set up")


class DatabaseSetupEvent(object):
    implements(IDatabaseSetupEvent)
    
    def __init__(self, metadata):
        self.metadata = metadata
