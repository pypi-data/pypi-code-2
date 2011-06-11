"""Useful blocks for visual rendering"""

import pygame

import serge.visual

class InvalidSprite(Exception): """The selected sprite was not valid"""

### Simple shapes ###

class Rectangle(serge.visual.Drawing):
    """A rectangle"""
    
    def __init__(self, (w, h), colour, thickness=0):
        """Initialise the rectangle"""
        super(Rectangle, self).__init__()
        self.width, self.height = w, h
        self.colour = colour
        self.thickness = thickness
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        pygame.draw.rect(surface, self.colour, (x, y, self.width, self.height), self.thickness)
        
        
class Circle(serge.visual.Drawing):
    """A circle"""
    
    def __init__(self, radius, colour, thickness=0):
        """Initialise the circle"""
        super(Circle, self).__init__()
        self.radius = radius
        self.colour = colour
        self.thickness = thickness
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        pygame.draw.circle(surface, self.colour, (x+self.radius, y+self.radius), self.radius, self.thickness)
        
        
### Shapes with text ###

class RectangleText(serge.visual.Drawing):
    """A rectangle with some text on it"""
    
    def __init__(self, text, text_colour, rect_dimensions, rect_colour, font_size=12, font_path='', thickness=0, justify='center'):
        """Initialise the drawing"""
        self.text_visual = serge.visual.Text(text, text_colour, font_path, font_size, justify)
        self.rect_visual = Rectangle(rect_dimensions, rect_colour, thickness)
        self.width = self.rect_visual.width
        self.height = self.rect_visual.height
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        w, h = self.rect_visual.width, self.rect_visual.height
        self.rect_visual.renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, (x+w/2-self.text_visual.width/2, y+h/2-self.text_visual.height/2))
        
class CircleText(serge.visual.Drawing):
    """A circle with some text on it"""
    
    def __init__(self, text, text_colour, radius, circle_colour, font_size=12, font_path='', thickness=0, justify='center'):
        """Initialise the drawing"""
        self.text_visual = serge.visual.Text(text, text_colour, font_path, font_size, justify)
        self.circle_visual = Circle(radius, circle_colour, thickness)
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        self.circle_visual.renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, 
            (x+self.circle_visual.radius-self.text_visual.width/2, 
             y+self.circle_visual.radius-self.text_visual.height/2))
        
### Sprite with text ###

class SpriteText(serge.visual.Sprite):
    """A sprite with some text on it"""

    def __init__(self, text, text_colour, sprite_name, font_size=12, font_path='', thickness=0, justify='center'):
        """Initialise the drawing"""
        self.text_visual = serge.visual.Text(text, text_colour, font_path, font_size, justify)
        sprite = serge.visual.Register.getItem(sprite_name)
        self.setImage(sprite.raw_image, (sprite.width, sprite.height), sprite.framerate, sprite.running)
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        super(SpriteText, self).renderTo(milliseconds, surface, (x, y))
        self.text_visual.renderTo(milliseconds, surface, 
                (x+self.width/2-self.text_visual.width/2, 
                 y+self.height/2-self.text_visual.height/2))

    def setText(self, text):
        """Set the text"""
        self.text_visual.setText(text)

    @property
    def text(self): return self.text_visual.text

class TextToggle(SpriteText):
    """A sprite text item that has multiple cells and can be used as a toggle
    
    You can set the cells directly of use On=0 and Off=1.
    
    """
    
    def __init__(self, *args, **kw):
        """Initialise the  TextToggle"""
        super(TextToggle, self).__init__(*args, **kw)
        #
        # Reality check - the underlying sprite must have at least two cells
        if len(self.cells) <= 1:
            raise InvalidSprite('The selected sprite does not have enough cells. Needs at least two')
        
    def setOn(self):
        """Set to on"""
        self.setCell(0)
        
    def setOff(self):
        """Set to off"""
        self.setCell(1)
        
    def toggle(self):
        """Toggle the state"""
        if self.current_cell == 0:
            self.setOff()
        else:
            self.setOn()
    
    def isOn(self):
        """Return if we are on"""
        return self.current_cell == 0
    
    def isOff(self):
        """Return if we are on"""
        return self.current_cell != 0
    
    
class Toggle(TextToggle):
    """Like a text toggle but with no text"""
    
    def __init__(self, sprite_name):
        """Initialise the toggle"""
        super(Toggle, self).__init__('', (0,0,0,0), sprite_name)
        
