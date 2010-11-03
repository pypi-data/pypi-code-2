from collections import defaultdict


class HierarView(object):
    """
    The goal of this view is to achieve a tree of responsabilities.


    Any node, subnode, subsubnode, etc of a HierarView are managed by
    it. 

    When another HierarView is encountered in the tree, this one
    becomes responsible for all its subnodes.

    TopModel [TopView]
     `-- ModelA
      `-- ModelA1
     `-- ModelB [BView]
      `-- ModelB1

    Here, TopView manages TopModel, ModelA and ModelA1 while BView
    manages ModelB and ModelB1.
    """
    _model2view = {}

    def __init__(self, aModel, aParentModel=None, aParentView=None,
                 theTopView=None):
        self._children_views = {}
        self._top_view = theTopView
        self._model = aModel
        self._parent_view = aParentView
        self._parent_model = aParentModel

        aModel.subscribe(self)

        for child in aModel.getChildren():
            self._traverse(child, aModel)

    def _instanciate_view(self, aModel, aParentModel):
        """
        Try to instanciate a view for a given model.
        """
        class_name = aModel.__class__.__name__

        # Try to mimic polymorphism using MROs
        if not class_name in self._model2view:
            parents = map(lambda s: s.__name__, aModel.__class__.__mro__)
            orig = parents.pop() # pop ourselves
            class_name = parents.pop() # pop first parent
            while parents and not class_name in self._model2view:
                class_name = parents.pop()
            if not class_name in self._model2view:
                return False

            self._model2view[orig] = self._model2view[class_name]

        # Instanciate view(s)
        for view_class in self._model2view[class_name]:
            new_view = None
            if self._top_view:
                new_view = self._top_view.getViewNode(aModel)
            if not new_view:
                new_view = view_class(aModel, aParentModel, self, self._top_view)
            if self._top_view:
                self._top_view.addViewNode(aModel, new_view)
            self._children_views[aModel.uuid] = new_view

        return True

    def _traverse(self, aModel, aParentModel):
        """
        Traverse, mirror and subscribe to a model.
        """
        # if we find a nested view, delegate work and return
        if self._instanciate_view(aModel, aParentModel):
            return

        aModel.subscribe(self)
        for child in aModel.getChildren():
            self._traverse(child, aModel)

    def _removeBranch(self, aModel):
        """
        Remove a branch from the view in reaction to a model branch
        removal (normally you remove the model instead).
        """
        if aModel.uuid in self._children_views:
            for child in aModel.getChildren():
                self._removeBranch(child)

            self._children_views[aModel.uuid].unlink()
            if self._top_view:
                self._top_view.delViewNode(aModel)
            del self._children_views[aModel.uuid]

    #-- Model callbacks --#
    def propertychange(self, aName, aValue):
        """
        Called when a property is changed in the model
        """    
        if hasattr(self.__class__, aName):
            setattr(self, aName, aValue)

    def addchild(self, aModel):
        """
        Called when a child is added to a watched model 
        """
        # FIXME: This is wrong, the parent is not always our root model !
        self._traverse(aModel, self._model)

    def delchild(self, aModel):
        """
        Called when a child is removed from our tree
        """
        self._removeBranch(aModel)

    #-- View Callbacks --#
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



class TopHierarView(HierarView):
    """
    Mandatory root node for a hierarchical view graph.
    """
    def __init__(self, aModel, aParentModel=None, aParentView=None):
        self._view_registry = {}
        HierarView.__init__(self, aModel, theTopView=self)

    def addViewNode(self, model, view):
        """
        Add a view node to the view.
        """
        self._view_registry[model.uuid] = view

    def delViewNode(self, model):
        """
        Delete a view node from the view.
        """
        del self._view_registry[model.uuid]


    def getViewNode(self, model):
        """
        Get the view node instantiated for the given model.
        """
        return self._view_registry.get(model.uuid, None)


