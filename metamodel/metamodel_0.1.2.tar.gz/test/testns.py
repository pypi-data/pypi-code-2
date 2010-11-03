import ns1
import ns2

from metamodel.meta import ClassRegistry


assert(ClassRegistry["ns1.AModel"] == ns1.AModel)
assert(ClassRegistry["ns2.AModel"] == ns2.AModel)

from metamodel.metamodel import Namespace, MetaModel, MetaProperty
from metamodel.dynamicmeta import Registry

ns = Namespace(name="foo")
ns2 = Namespace(name="foo2")
cls = MetaModel(name="foo",classname="foo")
cls2 = MetaModel(name="foo3",classname="foo3")

ns.addChild(cls)
ns.addChild(ns2)
ns2.addChild(cls2)
Registry.addChild(ns)

assert(ClassRegistry["foo.foo"])
assert(ClassRegistry["foo.foo2.foo3"])

# XXX test some kind of mutant cyclic namespace?

