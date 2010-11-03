from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property
from metamodel.meta import ClassRegistry
from metamodel.dynamicmeta import RegistryView

class WorldModel(SubscribableModel):
    """
    A world or sector.
    """
    name = Property(str,"unnamed")
    builds = ["ObjectModel"]

class ObjectModel(SubscribableModel):
    """
    An object.
    """
    name = Property(str,"unnamed object")
    builds = ["ObjectModel"]

class DerivedObjectModel(ObjectModel):
    pass

class DerivedObjectModel2(DerivedObjectModel):
    pass

class Another(SubscribableModel):
    builtby = ["ObjectModel"]

class Another2(SubscribableModel):
    builtby = ["DerivedObjectModel2"]

assert(WorldModel.get_builds() == set(["ObjectModel","DerivedObjectModel","DerivedObjectModel2"]))
assert(ObjectModel.get_builds() == set(["ObjectModel","DerivedObjectModel","DerivedObjectModel2","Another"]))
assert(DerivedObjectModel.get_builds() == set(["ObjectModel","DerivedObjectModel","DerivedObjectModel2","Another"]))
assert(DerivedObjectModel2.get_builds() == set(["ObjectModel","DerivedObjectModel","DerivedObjectModel2","Another","Another2"]))
assert(DerivedObjectModel2.get_builtby() == set(["WorldModel","ObjectModel","DerivedObjectModel","DerivedObjectModel2","Folder"]))
assert(ObjectModel.get_builtby() == set(["WorldModel","ObjectModel","DerivedObjectModel","DerivedObjectModel2","Folder"]))
assert(Another2.get_builtby() == set(["DerivedObjectModel2","Folder"]))
assert(Another.get_builtby() == set(["ObjectModel","DerivedObjectModel","DerivedObjectModel2","Folder"]))

# test registries
assert(WorldModel == ClassRegistry["WorldModel"])
assert(WorldModel == RegistryView.WorldModel)

# instance creation
w = WorldModel()
o = ObjectModel()
assert(w.name == "unnamed")
assert(o.name == "unnamed object")

# test event subscription
q = []
class Listener(object):
    def propertychange(self, name, value):
        assert(name == "name")
        assert(value == "test")
        q.append(1)
    def addchild(self, child):
        q.append(1)
    def delchild(self, child):
        q.append(1)

w.subscribe(Listener())

w.addChild(o)
assert(len(q) == 1)

w.delChild(o)
assert(len(q) == 2)

w.name = "test"
assert(len(q) == 3)

