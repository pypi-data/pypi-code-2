"""Some common classes and mixins"""

import random

version = '0.2.3'

import serge.blocks.effects

class MoveableBackground(object):
    """A mixin to give a moveable background"""
    
    
    def addEffects(self, obj=None):
        """Add effects to the screen"""
        #
        # Find a new scroll point
        while True:
            far_x = random.randint(100, 200)
            far_y = random.randint(100, 200)
            new_x = random.choice([-1, 1])*far_x + self.background.x
            new_y = random.choice([-1, 1])*far_y + self.background.y
            if (0 < new_x < 640) and (0 < new_y < 480):
                break
        #
        self.log.debug('New background location is %d, %d' % (new_x, new_y))
        #
        self.zoom_effect = serge.blocks.effects.MethodCallFade(self.background.visual.setScale, 2.0, 2.1, 5)
        self.x_effect = serge.blocks.effects.AttributeFade(self.background, 'x', self.background.x, new_x, 5, motion='accelerated')
        self.y_effect = serge.blocks.effects.AttributeFade(self.background, 'y', self.background.y, new_y, 5, 
                            done=self.addPause, motion='accelerated')
        #
        #self.world.addActor(self.zoom_effect)
        self.world.addActor(self.x_effect)
        self.world.addActor(self.y_effect)
        #

    def addPause(self, obj=None):
        """Add a pause in the effect"""
        self.pause = serge.blocks.effects.Pause(3, self.addEffects)
        self.world.addActor(self.pause)


    def addLogo(self, world):
        """Add a log to the page"""
        #
        self.logo = serge.actor.Actor('logo')
        self.logo.setSpriteName('logo')
        self.logo.moveTo(320, 50)
        self.logo.setLayerName('ui')
        world.addActor(self.logo)

    def niceTime(self, time):
        """Return a nice looking time"""
        return '%02d:%02d' % divmod(int(time), 60)
