import sys
import metamodel
import metamodel.dynamicmeta
from metamodel.metamodel import MetaProperty

Registry = metamodel.dynamicmeta.Registry
RegistryView = metamodel.dynamicmeta.RegistryView

# load the file
file = "test/todoontology.caf"
if len(sys.argv) > 1:
    file = sys.argv[1]
RegistryView.load_file(file)

# print classes found
#for ont in Registry.getChildren():
#    print " *",ont.name
#    for child in ont.getChildren():
#        print "  *",child.classname

#########################################
# test class loading
todotask = RegistryView.TodoTaskModel()
todothought = RegistryView.TodoThoughtModel()
todobug = RegistryView.TodoThoughtModel()

todo = RegistryView.TodoModel()
assert(todo.owner == [0,0,0]) # see if vector defaults are parsed sanely

assert(todotask.name == "a task")
assert(todotask.text == "default")

assert(issubclass(RegistryView.TodoBugModel, RegistryView.TodoTaskModel))

assert(RegistryView.TodoBugModel.get_builds() == set(["TodoTaskModel","TodoThoughtModel","TodoBugModel"] ))

#########################################
# test adding properties
prop = MetaProperty(name="test2",type="float",default=2.4)
todotask._model.addChild(prop)

prop = MetaProperty(name="test1",type="str",default="testdefault")
todotask._model.addChild(prop)

assert(todotask.test1 == "testdefault")
assert(todotask.test2 == 2.4)
todotask2 = RegistryView.TodoTaskModel()
todotask3 = RegistryView.TodoTaskModel()

# check defaults are there
assert(todotask2.test1 == "testdefault")
assert(todotask2.test2 == 2.4)

# set some values
todotask2.test1 = "test value"
assert(todotask2.test1 == "test value")
todotask3.test1 = "5.6"
assert(todotask3.test1 == "5.6")

# bad setting of uuid
try:
    todotask.uuid = "foo!"
    assert(False)
except:
    pass # ok!

#########################################
# test changing property declaration
test1prop = filter(lambda s: s.name == "test1",todotask._model.getChildren())[0]
oldval = getattr(todotask,"test1")

# change test property declaration
prop.name = "test3"
prop.default = "1.4"
prop.type = "float"

# check the changes are ok
assert(prop.name == "test3")
assert(prop.type == "float")
assert(prop.default == 1.4)

# check the old property name dissapeared
assert(hasattr(todotask,"test1") == False)

# check default remains default
assert(todotask.test3 == prop.default)
# check incompatible type becomes default
assert(todotask2.test3 == prop.default)
# check compatible type is converted
assert(todotask3.test3 == 5.6)

#########################################
# test deleting a property

q = []
class Listener(object):
    def __init__(self, model):
        model.subscribe(self)

    def delchild(self, child):
        q.append(1)

l =  Listener(todotask._model)
prop.invalidate() # destroy the property and trigger delChild in parent model.

assert(len(q) == 1)

assert(hasattr(todotask,"test3") == False)

#print todotask.__class__.get_builds()
#print todotask._model.builds_list
#print todotask._model.builtby_list


