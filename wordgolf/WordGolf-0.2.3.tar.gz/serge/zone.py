"""Zones are part of worlds"""

import math

import common 
import serialize
import geometry
pymunk = common.pymunk

class DuplicateActor(Exception): """An actor was already in the zone"""
class ActorNotFound(Exception): """Could not find the actor in the zone"""



class Zone(common.Loggable, geometry.Rectangle):
    """A zone
    
    A zone is part of a world. It is a container for objects
    and it controls whether objects will take part in world 
    updates.
    
    """
    
    my_properties = (
        serialize.B('active', False, 'whether the zone is active'),
        serialize.L('actors', set(), 'the actors in this zone'),
        serialize.F('physics_stepsize', 10.0, 'the size of physics steps in ms'),
        serialize.L('global_force', (0,0), 'the global force for physics'),
    )
    
    def __init__(self):
        """Initialise the zone"""
        self.addLogger()
        self.physics_stepsize = 10.0
        self.global_force = (0,0)
        self.active = False
        self.setSpatial(-1000, -1000, 2000, 2000)
        self.clearActors()
        self._initPhysics()

    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.addLogger()
        self.log.info('Initializing zone %s' % self)
        super(Zone, self).init()
        self._initPhysics()
        for actor in self.actors:
            actor.init()
            if actor.getPhysical():
                actor.getPhysical().init()
                self._addPhysicalActor(actor)
        

    ### Zones ###
    
    def updateZone(self, interval, world):
        """Update the objects in the zone"""
        #
        # Iterate through actors - use a list of the actors
        # in case the actor wants to update the list of
        # actors during this iteration
        for actor in list(self.actors):
            if actor.active:
                actor.updateActor(interval, world)
        #
        # Do physics if we need to
        if self._physics_objects:
            self._updatePhysics(interval)
            
    def addActor(self, actor):
        """Add an actor to the zone"""
        if actor in self.actors:
            raise DuplicateActor('The actor %s is already in the zone' % actor)
        else:
            self.actors.add(actor)
            if actor.getPhysical():
                self._addPhysicalActor(actor)

    def hasActor(self, actor):
        """Return True if the actor is in this zone"""
        return actor in self.actors
            
    def removeActor(self, actor):
        """Remove an actor from the zone"""
        try:
            self.actors.remove(actor)
        except KeyError:
            raise ActorNotFound('The actor %s was not in the zone' % actor)       
        else:
            if actor in self._physics_objects:
                self._physics_objects.remove(actor)
                p = actor.getPhysical()
                self.space.remove(p.body, p.shape)
                
    def clearActors(self):
        """Remove all actors"""
        self.actors = set()
        
    ### Finding ###
    
    def findActorByName(self, name):
        """Return the actor with the given name"""
        for actor in self.actors:
            if actor.name == name:
                return actor
        else:
            raise ActorNotFound('Could not find actor "%s"' % name) 
    
    def findActorsByTag(self, tag):
        """Return all the actors with a certain tag"""
        return [actor for actor in self.actors if actor.tag == tag]
    
    def findFirstActorByTag(self, tag):
        """Return the first actor found with the given tag or raise an error"""
        for actor in self.actors:
            if actor.tag == tag:
                return actor
        else:
            raise ActorNotFound('Could not find actor with tag "%s"' % tag) 

    def getActors(self):
        """Return all the actors"""
        return self.actors

    ### Rendering ###
    
    def renderTo(self, renderer, interval=0):
        """Render our objects to the renderer"""
        camera = renderer.getCamera()
        for actor in self.actors:
            if actor.active and camera.canSee(actor):
                try:
                    actor.renderTo(renderer, interval)
                except Exception, err:
                    self.log.error('Failed rendering "%s" actor "%s": %s' % (actor.tag, actor, err))
                    raise

    ### Physics ###
    
    def _initPhysics(self):
        """Initialize the physics engine"""
        #
        # Pymunk may not be installed - if so then we skip creating any physics context
        if not common.PYMUNK_OK:
            self.log.info('No pymunk - physics disabled')
            self._physics_objects = []
            return
        #
        # Create a context for the physics
        self.log.info('Initializing physics engine')
        self.space = pymunk.Space()
        self.space.add_collision_handler(2, 2, self._checkCollision, None, None, None)
        #
        # List of physics objects that we need to update
        self._physics_objects = []
        self._shape_dict = {}
                
    def _checkCollision(self, space, arbiter):
        """Return True if the collision should occur"""
        s1, s2 = arbiter.shapes[0], arbiter.shapes[1]
        #self.log.debug('Collision test for %s, %s' % (s1.group, s2.group))
        #if s1.group != s2.group:
        #    return False
        self._collisions.append((s1, s2))
        return True 
    
    def _addPhysicalActor(self, actor):
        """Add an actor with physics to the zone"""
        p = actor.getPhysical()
        self.space.add(p.body, p.shape)
        self._shape_dict[p.shape] = actor
        self._physics_objects.append(actor)
        actor.syncPhysics()
        
    def _updatePhysics(self, interval):
        """Perform a step of the physics engine"""
        #
        # Globally applied forces
        self.space.gravity = self.global_force
        #
        # Do calculations
        self._collisions = []
        while interval > 0.0:
            togo = min(self.physics_stepsize, interval)
            self.space.step(togo/1000.0)
            interval -= togo
        #
        # Apply all the collisions
        for shape1, shape2 in self._collisions:
            actor1, actor2 = self._shape_dict[shape1], self._shape_dict[shape2]
            actor1.processEvent(('collision', actor2))
            actor2.processEvent(('collision', actor1))
        #
        # Now update all the tracked objects in world space
        for actor in self._physics_objects:
            p = actor.getPhysical()
            actor.moveTo(*p.shape.body.position, no_sync=True)
            p.velocity = tuple(p.shape.body.velocity)
            
    def setPhysicsStepsize(self, interval):
        """Set the maximum step size for physics calculations"""
        self.physics_stepsize = interval
        
    def setGlobalForce(self, force):
        """Set the global force for physics"""
        self.global_force = force
        

