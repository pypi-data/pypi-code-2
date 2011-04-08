import zope.app.keyreference.interfaces
import zope.component
import zope.interface

import zc.freeze


class IDemo(zope.interface.Interface):
    """a demonstration interface for a demonstration class"""


class Demo(zc.freeze.Freezing):
    zope.interface.implements(IDemo)


class DemoKeyReference(object):
    zope.interface.implements(zope.app.keyreference.interfaces.IKeyReference)
    zope.component.adapts(IDemo)

    _class_counter = 0
    key_type_id = 'zc.freeze.DemoKeyReference'

    def __init__(self, context):
        self.context = context
        class_ = type(self)
        self._id = getattr(context, '__demo_key_reference__', None)
        if self._id is None:
            self._id = class_._class_counter
            context.__demo_key_reference__ = self._id
            class_._class_counter += 1

    def __call__(self):
        return self.context

    def __hash__(self):
        return (self.key_type_id, self._id)

    def __cmp__(self, other):
        if self.key_type_id == other.key_type_id:
            return cmp(self._id, other._id)
        return cmp(self.key_type_id, other.key_type_id)
