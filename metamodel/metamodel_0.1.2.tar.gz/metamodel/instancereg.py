"""
The instance registry notifies when instances with certain uuids
are created.

Basically here to allow for cross-referencing of instances from
different datasources.
"""

import uuid
from collections import defaultdict
from meta import SubscribableModelMeta, ClassRegistry

class _InstanceRegistry(object):
    def __init__(self):
        self._listeners = defaultdict(list)
        self._global_listeners = []

    def replace_listener(self, old_listener, new_listener):
        for listener in list(self._global_listeners):
            if hasattr(listener, "_obj") and listener._obj == old_listener:
                listener._obj = new_listener
        for section in self._listeners:
            section_list = self._listeners[section]
            for listener in section_list:
                if hasattr(listener, "_obj") and listener._obj == old_listener:
                    listener._obj = new_listener

    def subscribe(self, listener, uuid=None):
        if uuid:
            self._listeners[uuid].append(listener)
        else:
            self._global_listeners.append(listener)

    def post(self, obj):
        for listener in self._global_listeners:
            listener.uuidInstanced(obj)
        if obj.uuid in self._listeners:
            for listener in self._listeners[obj.uuid]:
                listener.uuidInstanced(obj)
            del self._listeners[obj.uuid]

InstanceRegistry = _InstanceRegistry()

class PropWaiter(object):
    """
    Base class for something that waits until an instance is present
    to fill in a property.
    """
    def __init__(self, uuid, obj, prop):
        InstanceRegistry.subscribe(self, uuid)
        self._obj = obj
        self._prop = prop
    def uuidInstanced(self, obj):
        setattr(self._obj, self._prop, obj)

class ChildWaiter(object):
    """
    Base class for something that waits until an instance is present
    to add a child.
    """
    def __init__(self, uuid, obj):
        InstanceRegistry.subscribe(self, uuid)
        self._obj = obj
    def uuidInstanced(self, obj):
        self._obj.addChild(obj)


