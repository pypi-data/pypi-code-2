from graphmodel import GraphModel
from metamodel.yamlserializer import SaveModel,LoadModel

if __name__ == "__main__":
    graphmodel = GraphModel()
    newnode = graphmodel.new("GraphNodeModel")
    q = []
    # subscribe
    class myevh(object):
        def propertychange(self,name,value):
            q.append(1)
        def addchild(self,child):
            q.append(1)
        def delchild(self,child):
            q.append(1)
    graphmodel.subscribe(myevh())
    newnode.subscribe(myevh())
    # change property
    newnode.name = "bla"
    assert len(q) == 1
    # add/remove node to graph
    graphmodel.addChild(newnode)
    assert len(q) == 2
    graphmodel.delChild(newnode)
    assert len(q) == 3
    graphmodel.addChild(newnode)
    assert len(q) == 4
    # add/remove connectors to graph
    newconnector = graphmodel.new("GraphNodeConnectorModel")
    newconnector.subscribe(myevh())
    newconnector.name = "bla"
    assert len(q) == 5
    assert newconnector.name == "bla"
    #assert newconnector.name == "bla" # XXX no magic for the moment
    newnode.addChild(newconnector)
    assert len(q) == 6
    newnode.delChild(newconnector)
    assert len(q) == 7
    newnode.addChild(newconnector)
    assert len(q) == 8
    # create connections
    newnode2 = graphmodel.new("GraphNodeModel")
    newconnector2 = graphmodel.new("GraphNodeConnectorModel")
    newnode2.addChild(newconnector2)
    newconnection = graphmodel.new("GraphConnectionModel",origin=newconnector,destination=newconnector2)
    graphmodel.addChild(newconnection)
    assert len(q) == 9
    graphmodel.delChild(newconnection)
    assert len(q) == 10
    graphmodel.addChild(newconnection)
    assert len(q) == 11
    newnode.addChild(newnode2)
    assert len(q) == 12

    #print " * model --> save --> data"
    data = SaveModel(graphmodel)
    #print data
    #print " * data --> load --> model2"
    graphmodel2 = LoadModel(data,"GraphModel")
    #print " * model2 --> save --> data2"
    data2 = SaveModel(graphmodel2[0])
    #print " * assert data == data2"
    assert data == data2

