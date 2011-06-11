"""Some effects which can alter properties of actors or visuals"""

import serge.actor

class InvalidMotion(Exception): """The motion type was not recognized"""


class Effect(serge.actor.Actor):
    """A generic effect"""
    
    def __init__(self, done=None, persistent=False):
        """Initialise the Effect"""
        super(Effect, self).__init__('effect')
        self.paused = False
        self.persistent = persistent
        self.done = done
        self.done_recorded = False
        
    def pause(self):
        """Pause the effect"""
        self.paused = True
        
    def unpause(self):
        """Unpause the effect"""
        self.paused = False
        
    def restart(self):
        """Restart the effect"""
        self.current = self.start
        
    def finish(self):
        """End the effect"""
        self.current = self.end

    def _effectComplete(self, world):
        """Record the fact that we are done"""
        if self.done and not self.done_recorded:
            self.log.debug('Actor %s is calling the done method (%s)' % (self.getNiceName(), self.done))
            self.done(self)
            self.log.debug('Actor %s completed the done method' % self.getNiceName())
        self.done_recorded = True
        if not self.persistent:
            world.removeActor(self)
        

class Pause(Effect):
    """A simple pause
    
    Used in conjunction with other effects. Calls the done method when
    the pause has completed.
    
    """
    
    def __init__(self, time, done, persistent=False):
        """Initialise the Pause"""
        super(Pause, self).__init__(done, persistent)
        self.time = time
        self.time_passed = 0.0
        
    def updateActor(self, interval, world):
        """Update this effect"""
        #
        # Do not do anything if we are paused
        if self.paused:
            return
        #
        # Record passing of time
        self.time_passed += interval/1000.0
        if self.time_passed >= self.time:
            self._effectComplete(world)
            

class MethodCallFade(Effect):
    """Repeated call a method linearly changing the parameter over time
    
    The attribute changes between a start and an end with a decay.
    The decay is the length of time taken to get from the start to the end.
    
    If persistent is set to true then the effect remains in the world to be
    re-used. If false then it will be removed when completed.
    
    A method can be provided through the done parameter which will be called
    when the effect has completed.
    
    The way the variable is moved is dependent on the motion type. This can
    be 'linear' or 'accelerated'.
    
    """    

    def __init__(self, method, start, end, decay, persistent=False, done=None, motion='linear'):
        """Initialise the AttributeFade"""
        super(MethodCallFade, self).__init__(done, persistent)
        self.method = method
        self.start = start
        self.end = end
        self.decay = decay
        self.current = self.start
        if motion not in ('linear', 'accelerated'):
            raise InvalidMotion('The motion type "%s" was not understood. Should be "linear" or "accelerated"' % motion)
        self.motion = motion
        self.acceleration = float(self.end - self.start)/((self.decay/2.0)**2)
        self.velocity = 0.0
        self.gone = 0.0
        
    def updateActor(self, interval, world):
        """Update this effect"""
        #
        # Do not do anything if we are paused
        if self.paused:
            return
        #
        # Update the current 
        initial = self.current
        if self.motion == 'linear':
            self.current -= float(interval)/(self.decay*1000.0) * (self.start - self.end)
        else:
            #
            # Are we accelerating or decelerating
            if self.gone >= self.decay/2.0:
                factor = -1
            else:
                factor = +1
            self.current += self.velocity*(float(interval)/1000.0) + 0.5*self.acceleration*(float(interval)/1000.0)**2
            self.velocity += factor*self.acceleration*(float(interval)/1000.0)
        self.gone += interval/1000.0
        #
        # Watch for the end
        if (self.start > self.end) and (self.current <= self.end) or \
           (self.start < self.end) and (self.current >= self.end):        
            self.current = self.end 
            self._effectComplete(world)
        #
        self.method(self.current)
        


class AttributeFade(MethodCallFade):
    """Linearly move an attribute
    
    The attribute changes between a start and an end with a decay.
    The decay is the length of time taken to get from the start to the end.
    
    If persistent is set to true then the effect remains in the world to be
    re-used. If false then it will be removed when completed.
    
    """
    
    def __init__(self, obj, attribute_name, *args, **kw):
        """Initialise the AttributeFade"""
        super(AttributeFade, self).__init__(self._doIt, *args, **kw)
        self.obj = obj
        self.attribute_name = attribute_name
                
    def _doIt(self, value):
        """Set the value"""
        setattr(self.obj, self.attribute_name, value)

