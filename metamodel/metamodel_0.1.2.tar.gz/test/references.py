from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property
import copy
class TestModel(SubscribableModel):
    pass

TEST = TestModel()

class TestModel2(SubscribableModel):
    ref1 = Property(TestModel)
    ref2 = Property(TestModel)
    ref3 = Property(TestModel)
    ref4 = Property(TestModel)

class TestModel3(SubscribableModel):
    ref5 = Property(TestModel)

# create some test objects
a = TestModel()
b = TestModel2()
c = TestModel2()
d = TestModel2()
e = TestModel3()
e.ref5 = TEST
assert(e.ref5 == TEST)
assert(e.getAllReferences() == [TEST])
# assign references
c.ref1 = a
c.ref2 = a
c.ref3 = b
c.ref4 = b
d.ref1 = a
d.ref2 = a
d.ref3 = b
d.ref4 = b
assert(b._referencedby["ref4"] == [c,d])
assert(set(c.getAllReferences()) == set([a,b]))

# check references
assert(c.ref1 == a)

# invalidate a
a.invalidate()
assert(c.ref1 == None)
assert(c.ref2 == None)
assert(d.ref1 == None)
assert(d.ref2 == None)
assert(c.ref3 == b)
assert(d.ref3 == b)

# unref un just one object
c.ref3 = None
assert(c.ref3 == None)
assert(d.ref3 == b)
# double unref
c.ref3 = None

# re-ref d.ref3
d.ref3 = e
assert(c.ref3 == None)
assert(d.ref3 == e)

assert(c.ref4 == b)
assert(d.ref4 == b)
b.invalidate()
assert(c.ref4 == None)
assert(d.ref4 == None)

