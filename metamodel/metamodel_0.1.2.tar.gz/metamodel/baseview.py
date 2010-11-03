"""
Base classes for a view structure.
"""

class ViewObjectBase(object):
    """
    Base class for a view object.

    Subscribes to the model, keeps some instance data, and notifies the
    ModelViewBase on changes to the graph.

    Subclasses are usually responsible for holding an instance representation in the view,
    owning the view engine specific object if necessary, and answering to model callbacks
    to update properties or modify parenting.
    """
    def __init__(self, view, parent, model):
        model.subscribe(self)
        self._view = view
        if parent:
            self._parents = [parent]
        else:
            self._parents = []
        self._model = model
        self._instance = None

    def getParentViews(self):
        """
        Get view nodes connected to the parent models.
        """
        views = []
        instances = self._view._instances
        for parent in self._parents:
            if parent:
                if parent.uuid in instances:
                    views.append(instances[parent.uuid])
        return views

    def getChildrenViews(self):
        """
        Get view nodes connected to the children models.
        """
        children = self._model.getChildren()
        instances = self._view._instances
        instanced = filter(lambda s: s.uuid in instances, children)
        children = map(lambda s: instances[s.uuid], instanced)
        return children
 
    # view "callbacks"
    def addparent(self, parent):
        """
        Add a parent node to this object.
        """
        self._parents.append(parent)

    def unlink(self):
        """
        Object unlinked from some parents.
        """
        pass

    # model callbacks
    def addchild(self, child):
        """addchild callback"""
        self._view.traverse(self._model, child)

    def delchild(self, child):
        """delchild callback"""
        self._view.removeBranch(self._model, child)
       
    def propertychange(self, name, value):
        """propertychange callback"""    
        if hasattr(self.__class__, name):
            setattr(self, name, value)

    def invalidate(self):
        """invalidate callback"""    
        self._model.unsubscribe(self)



class ModelViewBase(object):
    """
    Base class an engine view.

    Handles logic for traversing and recreating a model into the view.
    Creates view classes for the model based on the instance dict: _model2view.

    Subclasses are responsible for declaring their class mappings, and holding
    common data for the engine (all children get a pointer to the view).
    """
    _model2view = {}
    def __init__(self, model):
        self._model = model
        self._instances = {}
        self.traverse(None, model)
        model.subscribe(self)

    def getViewNode(self, model):
        """
        Get the view node instantiated for the given model.
        """
        return self._instances.get(model.uuid, None)

    def removeBranch(self, _, model):
        """
        Remove a branch from the view in reaction to a model branch
        removal (normally you remove the model instead).
        """
        if model.uuid in self._instances:
            for child in model.getChildren():
                self.removeBranch(model, child)
            self._instances[model.uuid].unlink()
            del self._instances[model.uuid]

    def traverse(self, parent, model, ctypes=None):
        """
        Traverse, mirror and subscribe to a model.
        """
        if model.uuid in self._instances and parent.uuid in self._instances:
            self._instances[model.uuid].addparent(parent)
        else:
            self.process(parent, model, ctypes)
            for child in model.getChildren():
                self.traverse(model, child, ctypes)

    def _is_child_of(self, model, ctypes):
        for ctype in ctypes:
            if isinstance(model, ctype):
                return True

    def process(self, parent, model, ctypes):
        """
        Generate a view node for a model.
        """
        if ctypes and not self._is_child_of(model, ctypes):
            return
        class_name = model.__class__.__name__
        if not class_name in self._model2view:
            parents = map(lambda s: s.__name__, model.__class__.__mro__)
            orig = parents.pop() # pop ourselves
            class_name = parents.pop() # pop first parent
            while parents and not class_name in self._model2view:
                class_name = parents.pop()
            if not class_name in self._model2view:
                return
            self._model2view[orig] = self._model2view[class_name]
        for klass in self._model2view[class_name]:
            inst = klass(self, parent, model)
            self._instances[model.uuid] = inst

    # model callbacks
    def addchild(self, child):
        """
        mm addchild callback.
        """
        self.traverse(self._model, child)

    def delchild(self, child):
        """
        mm delchild callback.
        """
        self.removeBranch(self._model, child)

