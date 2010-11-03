"""
Model overlays.

Provide facilities to create overlays over models, which can be synchronized
with the underlying model.
"""

from basemodel import SubscribableModel
from properties import Property

#######################################################################
# Node Watcher

class _NodeWatcher(object):
    """
    Watches over a model and its overlayed model to keep upload
    changes.
    """
    def __init__(self, overlay, stack, model, origmodel):
        self._model = model
        self._stack = stack
        self._overlay = overlay
        self._origmodel = origmodel
        self._origmodel.subscribe(self)
        self._state = 1
        self._props = {}

    def pushChanges(self):
        """
        Push changes upstream.
        """
        self._state = 0
        origchildren = list(self._origmodel.getChildren())
        # add children and check which where removed
        for child in self._model.getChildren():
            if not child in self._stack.values():
                # wasnt there before
                neworig = child.deepclone()
                self._origmodel.addChild(neworig)
                self._stack[neworig] = child
                watchers = self._overlay._watchers
                watchers[neworig] = _NodeWatcher(self._overlay,
                                                 self._stack,
                                                 child,
                                                 neworig)
            else:
                # still there
                for o, d in self._stack.items():
                    if d == child:
                        origchildren.remove(o)
        # remove nodes which have been deleted
        for remaining in origchildren:
            self._origmodel.delChild(remaining)
        # sync properties
        for prop in self._model._props:
            newval = getattr(self._model, prop)
            if not getattr(self._origmodel, prop)  == newval:
                setattr(self._origmodel, prop, newval)
        self._model._props = {}
        self._state = 1

    def overlay_deepclone(self, elmt):
        """
        Overlay a new element
        """
        if elmt in self._stack:
            newobj = self._stack[elmt]
        else:
            newobj = self._model.new(elmt.__class__, **elmt._props)
            self._overlay._watchers[elmt] = _NodeWatcher(self._overlay, self._stack, newobj, elmt)
            self._stack[elmt] = newobj
            for child in elmt.getChildren():
                newobj.addChild(self.overlay_deepclone(child))
        return newobj

    def propertychange(self, name, value):
        """
        A property changed in the upstream model.
        """
        return

    def addchild(self, child):
        """
        A child was added in the upstream model.
        """
        if not self._state:
            return
        clonedchild = self.overlay_deepclone(child)
        if not clonedchild in self._model.getChildren():
            self._model.addChild(clonedchild)

    def delchild(self, child):
        """
        A child was deleted from the upstream model.
        """
        if not self._state:
            return
        clonedchild = self._stack[child]
        self._model.delChild(clonedchild)

    def invalidate(self):
        """
        Upstream model has been invalidated.
        """
        self._model.invalidate()
        self._origmodel.unsubscribe(self)
        del self._overlay._watchers[self._origmodel]
        del self._stack[self._origmodel]

#######################################################################
# Persistence model capable of unpacking on dire conditions..

class OverlayElementMapping(SubscribableModel):
    """
    Root for the mappings from an overlay.
    """
    nchildren = Property(int, 0)

class OverlayMap(SubscribableModel):
    """
    A mapping from a upstream to overlay node.
    """
    origin = Property(SubscribableModel)
    destination = Property(SubscribableModel)

class OverlayModel(SubscribableModel):
    """
    Model for an overlay.
    """
    model = Property(SubscribableModel)
    shadow = Property(SubscribableModel)
    mapping = Property(SubscribableModel)
    def __init__(self, instance_uuid=None, datasource=None, topersist=0, **kwargs):
        self._state = 0
        self._topersist = topersist
        self._setprops = set()
        SubscribableModel.__init__(self, instance_uuid, datasource, **kwargs)
        self._state = 1
        if len(self._setprops) == len(self.properties):
            if len(self.mapping.getChildren()) == self.mapping.nchildren:
                self.becomeOverlay()
            else:
                self.mapping.subscribe(self)

    def addchild(self, _):
        """
        This function waits until mappings are filled up on loading.
        """
        if len(self.mapping.getChildren()) == self.mapping.nchildren:
            self.mapping.unsubscribe(self)
            self.becomeOverlay()

    def becomeOverlay(self):
        """
        Become an overlay now.
        """
        if self._topersist:
            return
        self._state = 0
        shadow = self.shadow
        mapping = self.mapping
        model = self.model
        self.__class__ = Overlay
        Overlay.__init__(self,
                              self.uuid, 
                              datasource=self._datasource, 
                              model=model, 
                              shadow=shadow, 
                              mapping=mapping)

    def setProperty(self, name, val):
        """
        Overloaded setProperty to keep an eye until all properties are set.
        """
        SubscribableModel.setProperty(self, name, val)
        if not val == None:
            self._setprops.add(name)
        if self._state and len(self._setprops) == len(self.properties):
            if len(self.mapping.getChildren()) == self.mapping.nchildren:
                self.becomeOverlay()
            else:
                self.mapping.subscribe(self)
        

#######################################################################
# The Overlay

class Overlay(SubscribableModel):
    """
    An overlay for a model.

    Must be initialized with a model to overlay (the "upstream" model)
    and will produce a perfect copy, which the user
    can modify, and push changes to upstream when desired, otherwise
    upstream property values are kept in sync so non changed properties
    look the same.

    Once created, the overlay will assume the class of the overlayed model
    and become completely transparent (the overlay api will still be present).

    Use like:
       overlay = Overlay(someModelInstance)
       overlay.someproperty = 5 # sets the property only on the overlay
       overlay.pushChanges() # push the changes to upstream.
       assert(overlay.__class__ == someModelInstance.__class) # overlay changed class
    """
    model = Property(SubscribableModel)
    def __init__(self, instance_uuid=None, datasource=None, **kwargs):
        SubscribableModel.__init__(self, instance_uuid, datasource, **kwargs)
        # check model is provided, otherwise err.
        if not "model" in kwargs:
            raise AttributeError,"Overlays have to be instanced with a model!"
        # set some initial variables
        self._overlaymodel = kwargs["model"]
        self._watchers = {}
        self._instmap = {}   
        if "shadow" in kwargs and "mapping" in kwargs:
            # overlay already prepared (or created from a model)
            self._instance = kwargs["shadow"]
            for inst_map in kwargs["mapping"].getChildren():
                newobj = inst_map.destination
                origin = inst_map.origin
                self._instmap[origin] = newobj
                self._watchers[origin] = _NodeWatcher(self, self._instmap, newobj, origin)
        else:
            # fresh overlay
            self._instance = self.overlay_deepclone(kwargs["model"], self._instmap)
        # hook up some functions, because we're going to change class soon.
        self.getProperty = self._getProperty
        self.setProperty = self._setProperty
        self.addChild = self._addChild
        self.delChild = self._delChild
        self.invalidate = self._invalidate
        self.pushChanges = self._pushChanges
        self.getChildren = self._getChildren
        self.getOverlayModel = self._getOverlayModel
        self.getOverlayInstance = self._getOverlayInstance
        self.getSelfToPersist = self._getSelfToPersist
        self.clone = self._clone
        self.deepclone = self._deepclone
        # now set the class to the upstream class
        self.__class__ = kwargs["model"].__class__
        self.__class__._instances.append(self) # publish ourselves with our class
        # hook overlay model core SubscribableModel properties on ourselves.
        self._children = self._instance._children
        self._props = {} #self._instance._props
        self._evhs = self._instance._evhs
        self._callbacks = self._instance._callbacks
        self._references = self._instance._references
        self._referencedby = self._instance._referencedby

    def pushChanges(self):
        """
        Push changes made to the overlay upstream.
        """
        self._pushChanges()

    def _getSelfToPersist(self):
        mapping = self.new(OverlayElementMapping,
                           nchildren=len(self._instmap))
        for key, val in self._instmap.iteritems():
            mapping.addChild(self.new(OverlayMap, 
                                      origin=key, 
                                      destination=val))
        return self.new(OverlayModel,
                                instance_uuid=self.uuid,
                                topersist=True,
                                model=self.getOverlayModel(),
                                shadow=self._instance,
                                mapping=mapping)

    def _clone(self):
        return self.new(Overlay, model=self.getOverlayModel())

    def _deepclone(self, stack=None):
        return self.new(Overlay, model=self.getOverlayModel().deepclone())

    def _getOverlayModel(self):
        return self._overlaymodel

    def _getOverlayInstance(self):
        return self._instance

    def _pushChanges(self):
        for watcher in list(self._watchers.values()):
            watcher.pushChanges()

    def _addChild(self, child):
        if not child in self._instance.getChildren():
            self._instance.addChild(child)

    def _getChildren(self):
        return self._instance.getChildren()

    def _invalidate(self, force=False):
        self._instance.invalidate(force)

    def _delChild(self, child):
        self._instance.delChild(child)

    def _getProperty(self, prop):
        try:
            return self._instance.getProperty(prop)
        except KeyError:
            return getattr(self._overlaymodel, prop)

    def _setProperty(self, prop, val):
        return self._instance.setProperty(prop, val)

    def overlay_deepclone(self, elmt, stack):
        if elmt in stack:
            newobj = stack[elmt]
        else:
            newobj = self.new(elmt.__class__, **elmt._props)
            elmt.__class__._instances.remove(newobj) # become "invisible"
            self._watchers[elmt] = _NodeWatcher(self, stack, newobj, elmt)
            stack[elmt] = newobj
            for child in elmt.getChildren():
                newobj.addChild(self.overlay_deepclone(child, stack))
        return newobj

