"""Classes to perform rendering"""

import pygame

import common
import serialize
import camera
import visual

class DuplicateLayer(Exception): """The layer was already present"""
class UnknownLayer(Exception): """The layer was not found"""


class Renderer(common.Loggable, serialize.Serializable):
    """The main rendering component"""
    
    my_properties = (
        serialize.L('layers', [], 'the layers we render to'),
        serialize.I('width', 640, 'the width of the screen'),
        serialize.I('height', 480, 'the height of the screen'),
        serialize.S('title', 'Serge', 'the title of the main window'),
        serialize.L('backcolour', (0,0,0), 'the background colour'),
        serialize.O('camera', None, 'the camera for this renderer'),
        serialize.O('icon', None, 'the icon for the main window'),
    )
    
    def __init__(self, width=640, height=480, title='Serge', backcolour=(0,0,0), icon=None):
        """Initialise the Renderer"""
        self.addLogger()
        self.width = width
        self.height = height
        self.title = title
        self.layers = []
        self.backcolour = backcolour
        self.camera = camera.Camera()
        self.camera.setSpatial(0, 0, self.width, self.height)
        self.icon = icon
        self.init()
            
    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""
        self.addLogger()
        self._sort_needed = False
        pygame.display.set_caption(self.title)
        self.surface = pygame.display.set_mode((self.width, self.height))
        for layer in self.layers:
            layer.setSurface(pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32))
        self.camera.init()
        self.camera.resizeTo(self.width, self.height)
        if self.icon:
            pygame.display.set_icon(visual.Register.getItem(self.icon).raw_image)
                
    ### Layers ###
    
    def addLayer(self, layer):
        """Add a layer to the rendering"""
        self.log.info('Adding layer "%s" at %d' % (layer.name, layer.order))
        if layer in self.layers:
            raise DuplicateLayer('The layer %s is already in the renderer' % layer)
        else:
            self.layers.append(layer)
        self._sort_needed = True
        layer.setSurface(pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32))

    def getLayer(self, name):
        """Return the named layer"""
        for layer in self.layers:
            if layer.name == name:
                return layer
        else:
            raise UnknownLayer('No layer with name "%s" was found' % name)

    def getLayers(self):
        """Return all the layers"""
        return self.layers
        
    def removeLayer(self, layer):
        """Remove the layer from the rendering"""
        try:
            self.layers.remove(layer)
        except ValueError:
            raise UnknownLayer('The layer %s was not found' % layer)

    def removeLayerNamed(self, name):
        """Remove the layer with the specific name"""
        layer = self.getLayer(name)
        self.removeLayer(layer)
        
    def clearLayers(self):
        """Clear all the layers"""
        self.layers = []
        
    def _sortLayers(self):
        """Sort the layers into the right order"""
        self.layers.sort(lambda l1, l2 : cmp(l1.order, l2.order))
        self._sort_needed = False

    def clearSurface(self):
        """Clear the surface"""
        self.surface.fill(self.backcolour)

    def preRender(self):
        """Prepare for new rendering"""
        for layer in self.layers:
            layer.clearSurface()
                
    def render(self):
        """Render all the layers"""
        self.clearSurface()
        if self._sort_needed:
            self._sortLayers()
        for layer in self.layers:
            if layer.active:
                layer.render(self.surface)

    def getSurface(self):
        """Return the overall surface"""
        return self.surface  
    
    def setCamera(self, camera):
        """Set our camera"""
        self.camera = camera    
        
    def getCamera(self):
        """Return our camera"""
        return self.camera  

    def getScreenSize(self):
        """Returns the screen size"""
        return (self.width, self.height)
    
    def snapshot(self, filename):
        """Take a snapshot of the screen"""
        pygame.image.save(self.surface, filename)
               
           
class Layer(common.Loggable, serialize.Serializable):
    """A layer on which to render things"""
    
    my_properties = (
        serialize.S('name', '', 'the name of the layer'),
        serialize.I('order', 0, 'the order to render (0=low)'),
        serialize.B('active', True, 'whether this layer is active'),
    )
    
    def __init__(self, name, order):
        """Initialise the Layer"""
        super(Layer, self).__init__()
        self.name = name
        self.order = order
        self.surface = None
        self.active = True


    ### Serializing ###
    
    def init(self):
        """Initialise from serialized state"""

    def setSurface(self, surface):
        """Set our surface"""
        self.surface = surface

    ### Rendering ###
          
    def clearSurface(self):
        """Clear our surface"""
        self.surface.fill((0,0,0,0))
          
    def render(self, surface):
        """Render to a surface"""
        surface.blit(self.surface, (0,0))
        
    def getSurface(self):
        """Return the surface"""
        return self.surface  
