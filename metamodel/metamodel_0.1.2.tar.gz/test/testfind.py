from metamodel import SubscribableModel, Property

# model for this test
class NamedModel(SubscribableModel):
    name = Property(str)
    reference = Property(SubscribableModel)

# setup a simple graph
a = NamedModel(name="a")
a.addChild(NamedModel(name="b"))
a.addChild(NamedModel(name="c"))
a.getChildren()[1].addChild(NamedModel(name="d"))
a.getChildren()[1].addChild(NamedModel(name="b"))
a.getChildren()[1].getChildren()[1].addChild(NamedModel(name="e"))
a.getChildren()[1].getChildren()[1].reference = NamedModel(name="ref")

# introduce circular references
a.getChildren()[1].getChildren()[1].addChild(a)
a.getChildren()[1].getChildren()[0].reference = a

# helper funcions
def printnames(aList):
    for obj in aList:
        print " *",obj.name, str(obj.uuid)

def assert_len(result, req_len):
    try:
        assert(len(result) == req_len)
    except:
        print "Wrong legth",result
        raise Exception

# Find b
assert_len(a.findChildren(name="b",recursive=True), 2)
# Find d
assert_len(a.findChildren(name="d",recursive=True), 1)
# Find e
assert_len(a.findChildren(name="e",recursive=True), 1)
# Find ref
assert_len(a.findChildren(name="ref",recursive=True), 1)
# Find ref Non recursive
assert_len(a.findChildren(name="ref"), 0)
# Find b Non recursive
assert_len(a.findChildren(name="b"), 1)
# Find d Non recursive
assert_len(a.findChildren(name="d"), 0)

