from zope import interface, component
from zope.publisher.interfaces.browser import IBrowserRequest

import interfaces
import traversing

@component.adapter(IBrowserRequest)
@interface.implementer(interfaces.ITraversalStackInfo)
def requestTraversalStackInfo(request):
    cons = request.annotations.get(traversing.CONSUMERS_ANNOTATION_KEY, [])
    return TraversalStackInfo(cons)

class TraversalStackInfo(tuple):
    interface.implements(interfaces.ITraversalStackInfo)

class BaseConsumer(object):
    interface.implements(interfaces.ITraversalStackConsumer)

    arguments = ()
    __name__ = None

    def __init__(self, context, request):
        self.context=context
        self.request=request

    def consume(self):
        stack = self.request.getTraversalStack()
        self.__name__ = stack.pop()
        consumed = [self.__name__]
        for name in self.arguments:
            v = stack.pop()
            consumed.append(v)
            setattr(self, name, v)
        self.request.setTraversalStack(stack)
        return consumed

    def __repr__(self):
        return '<%s named %r>' % (self.__class__.__name__,
                                  self.__name__)


