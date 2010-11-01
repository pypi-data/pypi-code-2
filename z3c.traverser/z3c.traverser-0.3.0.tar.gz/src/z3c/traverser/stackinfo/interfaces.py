from zope import interface, schema
from zope.interface.common.sequence import IExtendedReadSequence

class ITraversalStackInfo(IExtendedReadSequence):
    """A list of collected traversal stack consumers"""
    
class ITraversalStackConsumer(interface.Interface):
    """A traversal stack consumer"""

    __name__ = schema.TextLine(title=u'Name',
        description=u'The name under which the consumer is registered')
    
    arguments = schema.Tuple(title=u'Arguments',
        description=u'The argument names to be consumed')
    
    def consume():
        """consumes the items from the stack, and sets the __name__
        and attributes"""
