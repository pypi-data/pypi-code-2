"""
Metaclass for subscribable models.
"""

from collections import defaultdict
from properties import Property


class _ClassRegistry(object):
    """
    Class registry. All classes in the system can be queried here by name.
    """
    def __init__(self):
        self._values = {}
        self._listeners = defaultdict(list)
        self._global_listeners = []

    def subscribe(self, listener, name=None):
        """
        Subscribe to a certain class appearing, or to all classes
        if name is None.
        """
        if name:
            self._listeners[name].append(listener)
        else:
            self._global_listeners.append(listener)

    def post(self, name, obj):
        """
        Post a certain class appearing in the registry.
        """
        for listener in self._global_listeners:
            listener(obj)
        if name in self._listeners: 
            for listener in self._listeners[name]:
                listener(obj)
            del self._listeners[name]

    def values(self):
        """
        Get all values in the registry.
        """
        return self._values.values()

    def __setitem__(self, key, value):
        self._values[value.__module__+'.'+key] = value
        self._values[key] = value
        #self.post(key, value)

    def __contains__(self, key):
        return self._values.__contains__(key)

    def __getitem__(self, key):
        return self._values[key]

    def __iter__(self):
        for value in self._values:
            yield value

ClassRegistry = _ClassRegistry()
_ChildInfo = defaultdict(set)
_ParentInfo = defaultdict(set)
_PendingBuilderInfo = defaultdict(set)
_PendingBuiltbyInfo = defaultdict(set)

class SubscribableModelMeta(type):
    """
    Metaclass for subscribable models.

    Fills in some property and relation information,
    registers the class, and provides some api for the class.
    """
    def createClassModel(mcs):
        """
        Create the mm model for a python class.
        """
        try:
            from dynamicmeta import RegistryView
        except ImportError:
            # this is normal for the first "core" models, which have to be
            # created for the dynamic meta runtime to exist.
            return

        return RegistryView.createClassModel(mcs)

    def __new__(mcs, name, bases, dct, model=None):
        if not "abstract" in dct:
            dct["abstract"] = False
        acls =  type.__new__(mcs, name, bases, dct)
        ClassRegistry[name] = acls

        # save parents and childrens matrix
        for base in bases:
            _ParentInfo[name].add(base.__name__)
            _ChildInfo[base.__name__].add(name)
            for aparent in _ParentInfo[base.__name__]:
                _ChildInfo[aparent].add(name)
        
        # some uglyness to avoid putting the name in the
        # Property constructor.
        acls._instances = []
        acls.properties = []
        for propname in dir(acls):
            try:
                obj = getattr(acls, propname)
            except AttributeError:
                # its fine, some properties are write only
                continue
            if isinstance(obj, Property):
                obj.name = propname
                acls.properties.append(propname)

        # make sure builds is a set
        acls.builds = set(acls.builds)
        acls.builtby = set(acls.builtby)

        # fill in another classes builtby using class builds
        for builder_name in acls.builds:
            if builder_name in ClassRegistry:
                anothercls = ClassRegistry[builder_name]
                anothercls.builtby.add(name)
            else:
                _PendingBuiltbyInfo[builder_name].add(name)

        # fill in another classes builds using class builtby
        for builder_name in acls.builtby:
            if builder_name in ClassRegistry:
                anothercls = ClassRegistry[builder_name]
                anothercls.builds.add(name)
            else:
                _PendingBuilderInfo[builder_name].add(name)

        # check to see if we had built by subscriptions pending
        if name in _PendingBuilderInfo:
            for built_name in _PendingBuilderInfo[name]:
                acls.builds.add(built_name)
            _PendingBuilderInfo.pop(name)
        if name in _PendingBuiltbyInfo:
            for built_name in _PendingBuiltbyInfo[name]:
                acls.builtby.add(built_name)
            _PendingBuiltbyInfo.pop(name)

        if not model:
            model = acls.createClassModel()
        acls._model = model
        ClassRegistry.post(name, acls)

        return acls

    def get_builds(mcs):
        """
        Get the list of models building this model.
        """
        builds = set()
        for acls in mcs.__mro__:
            try:
                builds = builds.union(acls.builds)
            except AttributeError: # to avoid 'object' root
                continue
        for build in list(builds):
            childs = _ChildInfo[build]
            builds = builds.union(childs)
        return builds

    def get_builtby(mcs):
        """
        Get the list of built models for this model.
        """
        builds = set()
        for acls in mcs.__mro__:
            try:
                builds = builds.union(acls.builtby)
            except AttributeError: # to avoid 'object' root
                continue
        for build in list(builds):
            childs = _ChildInfo[build]
            builds = builds.union(childs)
        return builds

    def get_instances(mcs):
        """
        Get all instances for this class.
        """
        instances = list(mcs._instances)
        for acls in _ChildInfo[mcs.__name__]:
            instances += ClassRegistry[acls]._instances
        return instances
