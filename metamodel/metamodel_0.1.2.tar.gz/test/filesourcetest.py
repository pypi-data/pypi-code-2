from metamodel.datasources.filesource import FileDataSource
import metamodel
import uuid

source = FileDataSource(file="test/todoontology2.caf")
source2 = FileDataSource()

# check we're waiting for two instances of "d2d9da3c-c5c4-11dd-8f99-0013e8df9835"
assert(len(metamodel.basemodel.InstanceRegistry._listeners) == 1)
assert(len(metamodel.basemodel.InstanceRegistry._listeners[uuid.UUID('d2d9da3c-c5c4-11dd-8f99-0013e8df9835')]) == 1)

source2.file = "test/todoontology3.caf"

# check the instances where found
assert(len(metamodel.basemodel.InstanceRegistry._listeners) == 0)

source.save("/tmp/test1.caf")
source2.save("/tmp/test2.caf")
#for child in source.getChildren()[0]

