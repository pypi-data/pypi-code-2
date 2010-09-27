#
# Cocos
# http://code.google.com/p/los-cocos/
#

# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import pyglet

from cocos.director import director
from cocos.actions import Flip, Waves3D, ShuffleTiles
from cocos.sprite import Sprite
from cocos.layer import Layer, ColorLayer
from cocos.scene import Scene

class SpriteLayer ( Layer ):

    def __init__( self ):
        super( SpriteLayer, self ).__init__()

        sprite1 = Sprite( 'grossini.png' )
        sprite2 = Sprite( 'grossinis_sister1.png')
        sprite3 = Sprite( 'grossinis_sister2.png')

        sprite1.position = (400,240)
        sprite2.position = (300,240)
        sprite3.position = (500,240)

        self.add( sprite1 )
        self.add( sprite2 )
        self.add( sprite3 )

class BackgroundLayer( Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        self.img.blit(0,0)

if __name__ == "__main__":
    director.init( resizable=True )
    main_scene = Scene()

    back = BackgroundLayer()
    sprite = SpriteLayer()


    main_scene.add( back, z=0 )
    main_scene.add( sprite, z=1 )

    sprite.do( Waves3D(duration=4) + Flip(duration=4) )
    back.do( ShuffleTiles(duration=3, grid=(16,12)) )
    director.run (main_scene)
