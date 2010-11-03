# choose one of the following two
from metamodel.basemodel import SubscribableModel
from metamodel.properties import Property
#from dmvcmodel import DMVCSubscribableModel as SubscribableModel

########################################################
# graph interface

class GraphModel(SubscribableModel):
    name = Property(str,"a graph")

class GraphNodeModel(SubscribableModel):
    name = Property(str,"a graph node")

class GraphNodeConnectorModel(SubscribableModel):
    name = Property(str,"a graph connector")

class GraphConnectionModel(SubscribableModel):
    name = Property(str,"a graph connection")
    origin = Property(GraphNodeModel)
    destination = Property(GraphNodeModel)

