import metamodel
from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property
from metamodel.overlay import Overlay

class A(SubscribableModel):
    aprop = Property(str,"foo")

class B(SubscribableModel):
    aprop2 = Property(str,"foo")

aninst = A()
aninst.addChild(B())
aninst.addChild(B())

aprefab = Overlay(model=aninst)
aprefab2 = Overlay(model=aninst)

# initial tests...
assert(aprefab.__class__ == A)

assert(len(aprefab.getAllReferences()) == len(aninst.getAllReferences()))

assert(aprefab.getOverlayModel() == aninst)
assert(aprefab2.getOverlayModel() == aninst)

###################################################
# property checks

# set property on prefab
aprefab.aprop = "bla"
assert(aprefab.aprop == "bla")
assert(aprefab2.aprop == "foo")
assert(aninst.aprop == "foo")

# set property on factory
aninst.aprop = "foo2"

assert(aprefab.aprop == "bla")
assert(aprefab2.aprop == "foo2")
assert(aninst.aprop == "foo2")

# push prefab property
aprefab.pushChanges()

assert(aprefab.aprop == "bla")
assert(aprefab2.aprop == "bla")
assert(aninst.aprop == "bla")

# set property on prefab
aprefab.aprop = "bla2"
aprefab2.aprop = "bla3"
assert(aprefab.aprop == "bla2")
assert(aprefab2.aprop == "bla3")
assert(aninst.aprop == "bla")

# set property on factory
aninst.aprop = "foo3"

assert(aprefab.aprop == "bla2")
assert(aprefab2.aprop == "bla3")
assert(aninst.aprop == "foo3")

# push prefab changes
aprefab.pushChanges()

assert(aprefab.aprop == "bla2")
assert(aprefab2.aprop == "bla3")
assert(aninst.aprop == "bla2")

# push prefab changes
aprefab2.pushChanges()

assert(aprefab.aprop == "bla3")
assert(aprefab2.aprop == "bla3")
assert(aninst.aprop == "bla3")

###################################################
# children checks

# check children
assert(len(aprefab.getChildren()) == 2)
assert(len(aprefab2.getChildren()) == 2)
assert(len(aninst.getChildren()) == 2)

# add a child to factory
newchild = B()

aninst.addChild(newchild)

assert(len(aprefab.getChildren()) == 3)
assert(len(aprefab2.getChildren()) == 3)
assert(len(aninst.getChildren()) == 3)

# del child from factory
aninst.delChild(newchild)

assert(len(aprefab.getChildren()) == 2)
assert(len(aprefab2.getChildren()) == 2)
assert(len(aninst.getChildren()) == 2)

# add child to prefab
aprefab.addChild(B())

assert(len(aprefab.getChildren()) == 3)
assert(len(aprefab2.getChildren()) == 2)
assert(len(aninst.getChildren()) == 2)

# push changes to factory
aprefab.pushChanges()

assert(len(aprefab.getChildren()) == 3)
assert(len(aprefab2.getChildren()) == 3)
assert(len(aninst.getChildren()) == 3)

# delete a child from factory
aninst.delChild(aninst.getChildren()[-1])

assert(len(aprefab.getChildren()) == 2)
assert(len(aprefab2.getChildren()) == 2)
assert(len(aninst.getChildren()) == 2)

# delete a child from prefab instance
aprefab.delChild(aprefab.getChildren()[-1])

assert(len(aprefab.getChildren()) == 1)
assert(len(aprefab2.getChildren()) == 2)
assert(len(aninst.getChildren()) == 2)

aprefab.pushChanges()

assert(len(aprefab.getChildren()) == 1)
assert(len(aprefab2.getChildren()) == 1)
assert(len(aninst.getChildren()) == 1)

aninst.getChildren()[-1].invalidate()

assert(len(aprefab.getChildren()) == 0)
assert(len(aprefab2.getChildren()) == 0)
assert(len(aninst.getChildren()) == 0)

aninst.addChild(B())

assert(len(aprefab.getChildren()) == 1)
assert(len(aprefab2.getChildren()) == 1)
assert(len(aninst.getChildren()) == 1)

