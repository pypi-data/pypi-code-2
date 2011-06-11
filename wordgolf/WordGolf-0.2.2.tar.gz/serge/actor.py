"""The actor class"""

import pygame
import math

import common
import serialize
import geometry
import visual 

class Actor(common.Loggable, geometry.Rectangle):
    """Represents an actor"""
    
    my_properties = (
        serialize.S('tag', 'actor', 'the actor\'s tag'),
        serialize.S('name', '', 'the actor\'s name'),
        serialize.B('active', True, 'whether the actor is active'),
        serialize.S('sprite', '', 'the name of our sprite'),
        serialize.S('layer', '', 'the name of the layer we render to'),
        serialize.O('physical_conditions', '', 'the physical conditions for this object'),
        serialize.F('angle', 0.0, 'the angle for the actor'),
    )
    
    def __init__(self, tag, name=''):
        """Initialise the actor"""
        self.addLogger()
        super(Actor, self).__init__()
        # Whether we respond to updates or not
        self.active = True        
        # Class based tag to locate the actor by
        self.tag = tag
        # Unique name to locate by
        self.name = name
        # Our sprite
        self.sprite = ''
        self._visual = None
        # The layer we render to
        self.layer = ''    
        # Our zoom factor
        self.zoom = 1.0
        # Event handlers
        self.event_handlers = {}
        # Physics parameters - None means no physics
        self.physical_conditions = None
        # Angle
        self.angle = 0.0
        
    def init(self):
        """Initialize from serialized form"""
        self.addLogger()
        self.log.info('Initializing actor %s:%s:%s' % (self, self.tag, self.name))
        super(Actor, self).init()
        if self.sprite:
            self.setSpriteName(self.sprite)
        else:
            self._visual = None
        self.setLayerName(self.layer)
        self.zoom = 1.0

    def getNiceName(self):
        """Return a nice name for this actor"""
        if self.name:
            name_part = '%s (%s)' % (self.name, self.tag)
        else:
            name_part = self.tag
        return '%s [%s] <%s>' % (self.__class__.__name__, name_part, id(self))
        
    def setSpriteName(self, name):
        """Set the sprite for this actor"""
        self.visual = visual.Register.getItem(name).getCopy()
        self.sprite = name
        
    @property
    def visual(self): return self._visual
    @visual.setter
    def visual(self, value):
        """Set the visual item for this actor"""
        self._visual = value
        self._resetVisual()
        
    def _resetVisual(self):
        """Reset the visual item on the center point"""
        #
        # Adjust our location so that we are positioned and sized appropriately
        cx, cy, _, _ = self.getSpatialCentered()
        self.setSpatialCentered(cx, cy, self._visual.width, self._visual.height)
        #
        # Here is a hack - sometimes the visual width changes and we want to update our width
        # so we let the visual know about us so it can update our width. This is almost 
        # certainly the wrong thing to do, but we have some tests in there so hopefully
        # the right thing becomes obvious later!
        self._visual._actor_parent = self
        
    def getSpriteName(self):
        """Return our sprite"""
        return self.sprite
        
    def setAsText(self, text_object):
        """Set some text as our visual"""
        self.visual = text_object

    def setText(self, text):
        """Set the actual text"""
        self._visual.setText(text)
        
    def setLayerName(self, name):
        """Set the layer that we render to"""
        self.layer = name
    
    def getLayerName(self):
        """Return our layer name"""
        return self.layer
    
    def renderTo(self, renderer, interval):
        """Render ourself to the given renderer"""
        if self._visual:
            coords = renderer.camera.getRelativeLocation(self)
            if self.layer:
                self._visual.renderTo(interval, renderer.getLayer(self.layer).getSurface(), coords)
    
    def updateActor(self, interval, world):
        """Update the actor status"""

    def removedFromWorld(self, world):
        """Called when we are being removed from the world"""
        
    def setZoom(self, zoom):
        """Zoom in on this actor"""
        if self._visual:
            self._visual.scaleBy(zoom/self.zoom)
        self.zoom = zoom

    def setAngle(self, angle, sync_physical=False):
        """Set the angle for the visual"""
        if self._visual:
            self._visual.setAngle(angle)
            self._resetVisual()
        if sync_physical and self.physical_conditions:
            self.physical_conditions.body.angle = math.radians(-angle)
        self.angle = angle
        
    def getAngle(self):
        """Return the angle for the actor"""
        return self.angle
    
    def processEvent(self, event):
        """Process an incoming event"""
        #
        # Try to pass this off to a handler
        name, obj = event
        try:
            callback, arg = self.event_handlers[name]
        except KeyError:
            self.handleEvent(event)
        else:
            callback(obj, arg)
            
    def handleEvent(self, event):
        """Handle an incoming event"""
        pass
    
    def linkEvent(self, name, callback, arg=None):
        """Link an event to a callback"""
        self.event_handlers[name] = (callback, arg)
        
    def unlinkEvent(self, name):
        """Unlink an event from a callback"""
        del(self.event_handlers[name])

    ### Physics ###
    
    def setPhysical(self, physical_conditions):
        """Set the physical conditions"""
        #
        # Watch for if this object already has a shape
        if self.physical_conditions and self.physical_conditions.body:
            self.physical_conditions.updateFrom(physical_conditions)
        else:
            self.physical_conditions = physical_conditions
        
    def getPhysical(self):
        """Return the physical conditions"""
        return self.physical_conditions

    def syncPhysics(self, spatial_only=False):
        """Sync physics when the actors physical properties have been changed"""
        if self.physical_conditions:
            #self.log.debug('Syncing physics for %s to %s, %s' % (self.getNiceName(), self.x, self.y))
            self.physical_conditions.shape.body.position = self.x, self.y
            if not spatial_only:
                self.physical_conditions.shape.body.velocity = self.physical_conditions.velocity

    # Remap x, y properties to allow syncing with the physics engine

    def move(self, x, y):
        """Move by a certain amount"""
        super(Actor, self).move(x, y)
        self.syncPhysics(spatial_only=True)
        
    def moveTo(self, x, y, no_sync=False):
        """Move to a certain place"""
        super(Actor, self).moveTo(x, y)
        if not no_sync:
            self.syncPhysics(spatial_only=True)
          
