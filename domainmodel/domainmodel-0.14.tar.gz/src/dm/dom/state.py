import dm.exceptions
from dm.dom.base import *
from dm.dom.meta import *
from dm.ioc import *

class State(SimpleNamedObject):
    "Recorded state of StatefulObject instances."

    isConstant = True

    def __init__(self):
        super(State, self).__init__()
        self.behaviour = None

    def deleteObject(self, object):
        self.getBehaviour().deleteObject(object)

    def approveObject(self, object):
        self.getBehaviour().approveObject(object)

    def undeleteObject(self, object):
        self.getBehaviour().undeleteObject(object)

    def purgeObject(self, object):
        self.getBehaviour().purgeObject(object)

    class AbstractStateBehaviour(object):

        states = None
    
        def deleteObject(self, object):
            pass
            
        def approveObject(self, object):
            pass
            
        def undeleteObject(self, object):
            pass
            
        def purgeObject(self, object):
            pass
    
    class ActiveBehaviour(AbstractStateBehaviour):
    
        def deleteObject(self, object):
            object.deleteAggregates()
            object.raiseDelete()
            object.decacheItem()
            object.state = self.states['deleted']
            object.saveSilently()
            
        def purgeObject(self, object):
            message = 'An active object cannot be purged: %s' % str(object)
            raise dm.exceptions.KforgeDomError(message) 
    
    class DeletedBehaviour(AbstractStateBehaviour):
    
        def undeleteObject(self, object):
            object.decacheItem()
            object.state = self.states['active']
            object.saveSilently()
            object.raiseUndelete()
    
        def purgeObject(self, object):
            object.raisePurge()
            object.purgeAggregates()
            object.decacheItem()
            object.state = None 
            object.destroySelf()

    class PendingBehaviour(AbstractStateBehaviour):
    
        def approveObject(self, object):
            object.decacheItem()
            object.state = self.states['active']
            object.saveSilently()
            object.raiseApprove()
    
        def deleteObject(self, object):
            object.deleteAggregates()
            object.raiseDelete()
            object.decacheItem()
            object.state = self.states['deleted']
            object.saveSilently()
            
        def purgeObject(self, object):
            message = 'A pending object cannot be purged: %s' % str(object)
            raise dm.exceptions.KforgeDomError(message) 
    
    def getBehaviour(self):
        if not self.behaviour:
            self.checkBehavioursHaveStates()
            self.checkName()
            self.behaviour = self.createBehaviour()
        return self.behaviour

    def checkBehavioursHaveStates(self):
        abstractStateClass = State.__dict__['AbstractStateBehaviour']
        if not abstractStateClass.states:
            abstractStateClass.states = self.registry.states

    def checkName(self):
        if not self.name:
            raise Exception("State has no name: %s" % self)

    def createBehaviour(self):
        stateName = self.name
        behaviourClassName = stateName[0].upper()+stateName[1:]+'Behaviour' 
        behaviourClass = State.__dict__[behaviourClassName]
        return behaviourClass()

