"""Classes to handle sprites and other visual items"""

import pygame
import os
import copy

import common
import serialize
import registry

class BadSprite(Exception): """The sprite was not loaded"""
class InvalidCell(Exception): """The sprite cell number was out of range"""
class BadScale(Exception): """An invalid scaling factor was used"""
class InvalidJustification(Exception): """The justification was not recognized"""
class NotAllFilesFound(Exception): """Didn't find all the files when looking for a multi cell from files"""


class Store(registry.GeneralStore):
    """Stores sprites"""
    
    def _registerItem(self, name, path, w=1, h=1, framerate=0, running=False, rectangular=True, angle=0.0, zoom=1.0):
        """Register a sprite"""
        #
        # Watheight for special case h = -1 ... this is a multi cell
        if h == -1:
            return self.registerFromFiles(name, path, w, framerate, running, rectangular, angle, zoom)
        #
        # Reality heighteck
        if zoom <= 0.0:
            raise BadScale('The zoom factor for sprite %s was not >= 0' % name)
        #
        # Special case of no filename - we want to specify this layer
        if path != '':
            #
            # Load the image and work out the dimensions based on the number of cells
            # wide and high
            try:
                image = pygame.image.load(self._resolveFilename(path))
            except Exception, err:
                raise BadSprite('Failed to load sprite from "%s": %s' % (path, err))
            #
            s = self._registerImage(name, image, w, h, framerate, running, rectangular, angle, zoom)
        else:
            s = self.items[name] = None
        #
        # Remember the settings used to create the sprite
        self.raw_items.append([name, path, w, h, framerate, running, rectangular, angle, zoom])
        return s

    def _registerImage(self, name, image, w, h, framerate, running, rectangular, angle, zoom):
        """Register an image"""
        #
        if zoom != 1.0:
            image = pygame.transform.smoothscale(image, (int(image.get_width()*zoom), int(image.get_height()*zoom)))
        if angle != 0.0:
            image = pygame.transform.rotate(image, angle)
        #
        width = image.get_width()/w        
        height = image.get_height()/h
        #
        # Now load as a sprite sheet
        s = Sprite()
        #
        try:
            s.setImage(image, (width, height), framerate, running)
        except Exception, err:
            raise BadSprite('Failed to create sprite from "%s": %s' % (path, err))
        #
        # Set properties
        s.framerate = framerate
        s.running = running
        s.rectangular = rectangular   
        #
        self.items[name] = s         
        #
        return s
    
    def registerFromFiles(self, name, path, number, framerate=0, running=False, rectangular=True, angle=0.0, zoom=1.0):
        """Register a multi cell sprite from a number of files
        
        The path should be a string with a single numerical substitution.
        We will pass the numbers 1..number to this substitution to find
        the names of the files.
        
        """
        #
        # Generate a composite image - load the first one to find the size
        try:
            image = pygame.image.load(self._resolveFilename(path % 1))
        except Exception, err:
            raise BadSprite('Failed to load multi cell sprite from "%s": %s' % (path, err))
        #
        # Get size
        width = image.get_width()        
        height = image.get_height()
        #
        # Now create a canvas to load all the files onto
        canvas = pygame.Surface((number*width, height), pygame.SRCALPHA, 32)
        for i in range(1, number+1):
            try:
                image = pygame.image.load(self._resolveFilename(path % i))
            except Exception, err:
                raise NotAllFilesFound('Failed to load multi cell sprite from "%s": %s' % (path, err))
            canvas.blit(image, ((i-1)*width, 0))
        #
        # Ok, now create as if normal
        s = self._registerImage(name, canvas, number, 1, framerate, running, rectangular, angle, zoom)
        #
        # Special case of h = -1 to trigger logic in the registerItem method when we are recovering from
        # a serialize
        self.raw_items.append([name, path, number, -1, framerate, running, rectangular, angle, zoom])
        #
        return s
                 
Register = Store()


class Drawing(object):
    """Represents something to draw on the screen"""

    def __init__(self):
        """Initialise the drawing"""
        self._alpha = 1.0
        self.width = 0.0
        self.height = 0.0
            
    def scaleBy(self, factor):
        """Scale the image by a factor"""
        raise NotImplementedError
            
    def setAngle(self, angle):
        """Set the rotation to a certain angle"""
        raise NotImplementedError
    
    ### Rendering ###
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        raise NotImplementedError

    def setAlpha(self, alpha):
        """Set the overall alpha"""
        raise NotImplementedError

    def _setAlphaForSurface(self, surface, alpha):
        """Set the alpha for a surface"""
        size = surface.get_size()
        for y in xrange(size[1]):
            for x in xrange(size[0]):
                r,g,b,a = surface.get_at((x,y))
                surface.set_at((x,y),(r,g,b,int(a*alpha)))
        return surface

    @property
    def alpha(self): return self._alpha
    @alpha.setter
    def alpha(self, alpha): self.setAlpha(alpha)
    
    ### Copying ###
    
    def getCopy(self):
        """Return a copy"""
        return copy.copy(self)
    
    
class Sprite(Drawing):
    """An object that gets drawn on the screen"""
    
    def getCopy(self):
        """Return a copy of this sprite"""
        new = self.__class__()
        new.setImage(self.raw_image, (self.width, self.height), self.framerate, self.running)
        return new

    def setAlpha(self, alpha):
        """Set the overall alpha"""
        self.setCells()
        for idx, cell in enumerate(self.cells):
            self._setAlphaForSurface(cell, alpha)
        self._alpha = alpha

    def setImage(self, image, (width, height), framerate=0, running=False):
        """Set the image of this sprite"""
        #
        # Store raw image
        self.raw_image = image
        self.width = self.raw_width = width
        self.height = self.raw_height = height
        self.cx = self.raw_cx = width/2
        self.cy = self.raw_cy= height/2
        #
        self.framerate = framerate
        self.frame_time = 0 if framerate == 0 else 1000.0/framerate
        self.running = running
        self.last_time = 0
        self.direction = 1
        self.zoom = 1.0
        self.angle = 0.0
        #
        self.setCells()
        self.current_cell = 0
        self._alpha = 1.0
        
    ### Cells ###
        
    def setCells(self):
        """Set the cells of the animation"""
        #
        # Make cells
        self.cells = []
        rows = self.raw_image.get_height()/self.raw_height
        cols = self.raw_image.get_width()/self.raw_width
        #
        self.cells = []
        raw_image = self.raw_image.copy()
        for row in range(rows):
            for col in range(cols):
                r = pygame.Rect(col*self.raw_width, row*self.raw_height, self.raw_width, self.raw_height)
                img = raw_image.subsurface(r)
                if self.zoom != 1.0:
                    img = pygame.transform.smoothscale(img, (int(img.get_width()*self.zoom), int(img.get_height()*self.zoom)))
                if self.angle != 0.0:
                    img = pygame.transform.rotate(img, self.angle)
                self.cells.append(img)
        #
        if self.cells:
            self.width = self.cells[0].get_width()
            self.height = self.cells[0].get_height()
            self.cx = self.width/2
            self.cy = self.height/2

    def setCell(self, number):
        """Set the current cell number"""
        if 0 <= number < len(self.cells):
            self.current_cell = number
        else:
            raise InvalidCell('Cell number %d is out of range for this sprite' % number)
        
        
    ### Deformations ###
    
    def scaleBy(self, factor):
        """Scale the image by a factor"""
        if factor <= 0:
            raise BadScale('Scaling factor must be >= 0')
        self.zoom *= factor
        self.setCells()

    def setScale(self, scale):
        """Set the scaling to a certain factor"""
        self.scaleBy(scale/self.zoom)
                    
    def setAngle(self, angle):
        """Change the angle - returning the amount by which the sprite has shifted"""
        self.angle = angle
        self.setCells()
    
    ### Rendering ###
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        #
        # Update current frame
        if self.framerate and self.running:
            self.last_time += milliseconds
            if self.last_time >= self.frame_time:
                self.last_time -= self.frame_time
                self.current_cell += self.direction
                if self.current_cell <= 0:
                    self.current_cell = 0
                    self.direction = 1
                elif self.current_cell >= len(self.cells)-1:
                    self.current_cell = len(self.cells)-1
                    self.direction = -1       
        #
        # Draw to the surface
        surface.blit(self.cells[self.current_cell], (x, y))
        
class Text(Drawing):
    """Some text to display"""
    
    def __init__(self, text, colour, font_path='', font_size=12, justify='center'):
        """Initialise the text"""
        super(Text, self).__init__()
        # 
        # Hack - see below
        self._actor_parent = None
        #
        self.colour = colour if len(colour) == 4 else (colour + (255,))
        self.text = text
        self.font_size = font_size
        self.angle = 0.0
        self.font_path = font_path if font_path else pygame.font.get_default_font()
        self.font = pygame.font.Font((font_path if font_path else pygame.font.get_default_font()), font_size)
        self.setText(text)
        self.justify = justify
        
    def setJustify(self, justify):
        """Set the justification"""
        setting = justify.lower()
        if setting not in ('left', 'center'):
            raise InvalidJustification('Justification not recognized (%s)' % justify)
        self.justify = setting
        
    def setText(self, text):
        """Set our text"""
        #
        # Break into lines and then render each one
        if text == '':
            text = ' '
        lines = text.splitlines()
        #
        # Find out how wide to make our surface
        max_length, long_line = max([(len(line), line) for line in lines])       
        test_text = self.font.render(long_line, True, self.colour)
        width = test_text.get_width()
        height = self.font.get_height()
        #
        # Now make a surface
        self.surface = pygame.Surface((width, height*len(lines)), pygame.SRCALPHA, 32)
        #
        # And write all our text
        for idx, line in enumerate(lines):
            self.surface.blit(self.font.render(line, True, self.colour), (0, height*idx))
        #
        if self.angle != 0:
            self.surface = pygame.transform.rotate(self.surface, self.angle)
        self.width = self.surface.get_width()
        self.height = self.surface.get_height()
        #
        # Hack to get the actor to spot that we updated our width
        if self._actor_parent:
            self._actor_parent.resizeTo(self.width, self.height)
        #
        self.text = text

    def setFontSize(self, size):
        """Set the font size"""
        self.font_size = size
        self.font = pygame.font.Font((font_path if font_path else pygame.font.get_default_font()), font_size)

    def setColour(self, colour):
        """Set the colour"""
        self.colour = colour
        self.setText(self.text)
                
    def setFontSize(self, font_size):
        """Set our font size"""
        self.font_size = font_size
        self.font = pygame.font.Font(self.font_path, font_size)
        self.setText(self.text)

    def setAlpha(self, alpha):
        """Set our alpha"""
        self.setText(self.text)
        self._setAlphaForSurface(self.surface, alpha)
        self._alpha = alpha
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        if self.justify == 'left':
            surface.blit(self.surface, (x+self.width/2, y+self.height/2))
        else:
            surface.blit(self.surface, (x, y))
        
    def setAngle(self, angle):
        """Rotate our sprite by a certain angle"""
        self.angle = angle
        self.setText(self.text)
        
    def scaleBy(self, scale):
        """Scale our sprite by a certain certain amount"""
        self.setFontSize(self.font_size*scale)
