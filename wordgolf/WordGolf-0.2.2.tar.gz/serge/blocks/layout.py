"""Blocks to help with laying out things on the screen"""

import serge.actor
import serge.engine

class OutOfRange(Exception): """Tried to find something outside the range of the container"""
class CellOccupied(Exception): """Tried to put an actor in an occupied cell"""
class CellEmpty(Exception): """The cell being accessed was empty"""
class UnknownActor(Exception): """The actor was not found"""

class Container(serge.actor.Actor):
    """A layout container that contains actors"""

    def __init__(self, tag, name='', width=None, height=None):
        """Initialise the Bar"""
        super(Container, self).__init__(tag, name)
        #
        # Default sizes are the extent of the screen
        engine = serge.engine.CurrentEngine()
        if width is None:
            width = engine.getRenderer().getScreenSize()[0]
        if height is None:
            height = engine.getRenderer().getScreenSize()[1]
        #
        # Set our size
        self.resizeTo(width, height)
        # Stored changes that we need to send to the world
        self._changes = []
        
        
    def updateActor(self, interval, world):
        """Update the bar
        
        We need to send pending changes to the world.
        
        """
        while self._changes:
            change, actor = self._changes.pop()
            if change == 'add':
                world.addActor(actor)
            elif change == 'remove':
                world.removeActor(actor)
            else:
                raise ValueError('Unknown change "%s" to %s' % (change, actor))

    def removedFromWorld(self, world):
        """The bar is being removed from the world
        
        This will remove all the actors that are in the bar.
        
        """
        self.log.info('Removing all actors from %s' % self.getNiceName())
        for actor in self.iterActors():
            world.removeActor(actor)            

    def setLayerName(self, name):
        """Set the layer name"""
        super(Container, self).setLayerName(name)
        for actor in self.iterActors():
            actor.setLayerName(name)    

    def iterActors(self):
        """Return all the actors in this container"""
        raise NotImplementedError


class Bar(Container):
    """A bar of actors - useful for user interfaces"""
    
    def __init__(self, tag, name='', width=None, height=None):
        """Initialise the Bar"""
        super(Bar, self).__init__(tag, name, width, height)
        # The actors in the bar
        self._actors = []
        
    def addActor(self, actor):
        """Add an actor to the bar"""
        self._actors.append(actor)
        self._changes.append(('add', actor))
        self._redoLocations()
        actor.setLayerName(self.getLayerName())
        
    def iterActors(self):
        """Iterate through the actors"""
        return self._actors

    
class HorizontalBar(Bar):
    """A horizontal bar of actors"""
    
    def _redoLocations(self):
        """Reset the locations of the objects within us"""
        self.log.info('Resetting locations')
        width = float(self.width) / len(self._actors)
        left, top, _, _ = self.getSpatial()
        for i, actor in enumerate(self._actors):
            actor.moveTo(left + width*(i+0.5), top + self.height*0.5)
            self.log.debug('Set %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))
        
class VerticalBar(Bar):
    """A vertical bar of actors"""
    
    def _redoLocations(self):
        """Reset the locations of the objects within us"""
        self.log.info('Resetting locations')
        height = float(self.height) / len(self._actors)
        left, top, _, _ = self.getSpatial()
        for i, actor in enumerate(self._actors):
            actor.moveTo(left + self.width*0.5, top + height*(i+0.5))
            self.log.debug('Set %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))


class Grid(Container):
    """A grid of actors"""
    
    def __init__(self, tag, name='', size=(1,1), width=None, height=None):
        """Initialise the Grid"""
        super(Grid, self).__init__(tag, name, width, height)
        self._grid = []
        self.setGrid(size)
        
    def setGrid(self, (w, h)):
        """Set the size of the grid
        
        This also removes all the current actors from the world. Note that
        this can be tricky if you want to re-add some of the actors since
        the actors are not actually removed until the next world update
        and so you cannot re-add them before this or you will get a duplicate
        actor error from the world.
        
        """
        self.clearGrid()
        self._grid = []
        for row in range(w):
            self._grid.append([])
            for col in range(h):
                self._grid[-1].append(None)
        self.rows, self.cols = h, w

    def clearGrid(self):
        """Clear the entire grid"""
        for x, row in enumerate(self._grid):
            for y, actor in enumerate(row):
                if actor is not None:
                    self.removeActor((x, y))
       
    def addActor(self, (x, y), actor):
        """Add an actor to the grid"""
        #
        # Make sure that there isn't something already there
        try:
            occupant = self.getActorAt((x, y))
        except CellEmpty:
            pass
        else:
            raise CellOccupied('The cell %s is already occupied by %s in grid %s' % ((x, y), occupant.getNiceName(), self.getNiceName()))
        #
        # Add to the grid
        try:
            self._grid[x][y] = actor
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        #
        # Now make sure that we update everything
        self._changes.append(('add', actor))
        actor.setLayerName(self.getLayerName())
        actor.moveTo(*self._getCoords((x, y)))
        self.log.debug('Set coords for %s to %d, %d' % (actor.getNiceName(), actor.x, actor.y))

    def getActorAt(self, (x, y)):
        """Return the actor at a certain location"""
        try:
            occupant = self._grid[x][y]
        except IndexError:
            raise OutOfRange('%s is out of the range of this grid (%s)' % ((x, y), self.getNiceName()))
        else:
            if occupant is None:
                raise CellEmpty('The cell %s in grid %s is empty' % ((x, y), self.getNiceName()))
            else:
                return occupant

    def findActorLocation(self, actor):
        """Find the location of an actor"""
        for x, row in enumerate(self._grid):
            for y, test_actor in enumerate(row):
                if actor == test_actor:
                    return (x, y)
        else:
            raise UnknownActor('The actor %s was not found in grid %s' % (actor.getNiceName(), self.getNiceName()))
        
    def removeActor(self, (x, y)):
        """Remove the actor at a certain location"""
        try:
            occupant = self.getActorAt((x, y))
        except:
            raise
        else:
            self._grid[x][y] = None
            self._changes.append(('remove', occupant))
        
   
    def _getCoords(self, (x, y)):
        """Return the coordinates of a location"""
        my_x, my_y, w, h = self.getSpatial()
        return (my_x + (x+0.5)*w/self.cols, my_y + (y+0.5)*h/self.rows)
       
    def iterActors(self):
        """Iterate through all our actors"""
        for row in self._grid:
            for actor in row:
                if actor is not None:
                    yield actor
                
