"""The sound classes"""

import pygame

import common
import serialize
import registry 

class UnknownSound(Exception): """The sound was not found"""
class BadSound(Exception): """Could not load sound from"""


class Store(registry.GeneralStore):
    """Stores sounds"""
    
    def _registerItem(self, name, path):
        """Register the sound"""
        #
        # Load the sound
        try:
            sound = pygame.mixer.Sound(self._resolveFilename(path))
        except Exception, err:
            raise BadSound('Failed to load sound from "%s": %s' % (path, err))
        
        #
        # Remember the settings used to create the sprite
        self.raw_items.append([name, path])
        self.items[name] = sound
        return sound
    
    def playSound(self, name):
        """Play a sound"""
        self.getItem(name).play()
    


Register = Store()

