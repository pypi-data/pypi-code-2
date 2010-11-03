"""
Instance guardian.

Listens to objects to replicate changes on the network.
It is more client oriented, but some code can be reused for the server
"""
from metamodel import SubscribableModel

class InstanceGuardian(object):
    """
    A model guardian.
    """
    def __init__(self, model, datasource):
        self._model = model
        self._datasource = datasource
        self._model.subscribe(self)

    # events from the model
    def get_proto(self):
        """
        Get the client protocol object.
        """
        return self._datasource._proto
    
    def propertychange(self, name, value):
        """
        Callback for property change.
        """
        if not self.get_proto().state == 1:
            return
        if isinstance(value, SubscribableModel):
            print "propchange",value,value._datasource,self._datasource
            if value._datasource == self._datasource:
                print "send refchange",value
                self.get_proto().sendReferenceChange(self._model, name, value)
        else:
            self.get_proto().sendPropertyChange(self._model, name, value)

    def addchild(self, child):
        """
        Callback for child addition.
        """
        if not child._datasource == self._datasource:
            return # its not our node
        if not self.get_proto().state == 1:
            return
        self.get_proto().sendAddChild(self._model, child)

    def delchild(self, child):
        """
        Callback for child removal.
        """
        if not child._datasource == self._datasource:
            return # its not our node
        if not self.get_proto().state == 1:
            return
        self.get_proto().sendDelChild(self._model, child)

    def invalidate(self):
        """
        Callback for invalidate.
        """
        if not self.get_proto().state == 1:
            return
        self.get_proto().sendInvalidate(self._model)


