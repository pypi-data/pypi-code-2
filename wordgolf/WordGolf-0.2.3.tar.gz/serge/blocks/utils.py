"""Some utilities that speed up common operations"""

import serge.render
import serge.actor

def createLayersForEngine(engine, layers):
    """Add a number of layers to the engine
    
    The layers parameter is a list of layer names. The layers are added to
    the renderer of the engine as successive layers in order.
    
    """
    renderer = engine.getRenderer()
    #
    # Find the right number of layers so that we can set the order correctly
    n = len(renderer.getLayers())
    for name in layers:
        layer = serge.render.Layer(name, n)
        renderer.addLayer(layer)
        n += 1
        
        
def createWorldsForEngine(engine, worlds):
    """Add a numer of worlds to the engine
    
    The words parameter is a list of names of the worlds to create.
    Each world is created with a single active zone which is quite
    large.
    
    """
    for name in worlds:
        world = serge.world.World(name)
        zone = serge.zone.Zone()
        zone.active = True
        zone.setSpatial(-2000, -2000, 4000, 4000)
        world.addZone(zone)
        engine.addWorld(world)
        

def addSpriteActorToWorld(world, tag, name, sprite_name, layer_name, center_position=None, physics=None):
    """Create a new actor in the world and set the visual to be the named sprite
    
    If the center position is not specified then it is placed at the center of the screen.
    
    """
    #
    # If not position then put at the center
    if center_position is None:
        renderer = serge.engine.CurrentEngine().getRenderer()
        center_position = (renderer.width/2.0, renderer.height/2.0)
    #
    # Create the new actor
    actor = serge.actor.Actor(tag, name)
    actor.setSpriteName(sprite_name)
    actor.setLayerName(layer_name)
    if physics:
        actor.setPhysical(physics)
    actor.moveTo(*center_position)
    world.addActor(actor)
    return actor

def addVisualActorToWorld(world, tag, name, visual, layer_name, center_position=None, physics=None):
    """Create a new actor in the world and set the visual 
    
    If the center position is not specified then it is placed at the center of the screen.
    
    """
    #
    # If not position then put at the center
    if center_position is None:
        renderer = serge.engine.CurrentEngine().getRenderer()
        center_position = (renderer.width/2.0, renderer.height/2.0)
    #
    # Create the new actor
    actor = serge.actor.Actor(tag, name)
    actor.visual = visual
    actor.setLayerName(layer_name)
    if physics:
        actor.setPhysical(physics)
    actor.moveTo(*center_position)
    world.addActor(actor)
    return actor

