"""Graphical game of golf words"""

import serge.engine
import serge.world
import serge.actor
import serge.zone
import serge.render
import serge.sound 
try:
    import serge.builder.builder
except ImportError:
    pass

import game
import gameover
import keypad 
import gamestart
import helppage
import escapepage
import scorespage

def main(options, args):
    """Run the game"""
    #
    # Debug options
    if options.any:
        game.Game.check_spelling = False
    if options.suggest:
        keypad.KeyPad.can_suggest = True
    gamestart.Start.possible_holes = map(int, options.holes.split(','))
    
    ### Sounds ###

    serge.sound.Register.setPath('sound')
    r = serge.sound.Register.registerItem
    r('start', 'start.wav')
    r('begin', 'begin.wav')
    r('letter', 'letter.wav')
    r('word', 'word.wav')
    r('hole', 'hole.wav')
    r('good-hole', 'good_hole.wav')
    r('poor-hole', 'poor_hole.wav')
    r('unletter', 'unletter.wav')
    r('error', 'error.wav')
    r('bad-letter', 'badletter.wav')
    r('end-game', 'end_game.wav')
    r('sand', 'sand.wav')
    r('water', 'water.wav')

    ### Graphics ###

    serge.visual.Register.setPath('graphics')
    r = serge.visual.Register.registerItem
    rf = serge.visual.Register.registerFromFiles
    r('start-bg', 'start_bg.png')
    r('course', 'course1.png')
    r('hole2', 'hole1.png')
    r('hole1', 'hole1.png')
    r('logo', 'logo.png')
    rf('game1', 'game1_%d.png', 2)
    rf('game2', 'game2_%d.png', 2)
    rf('game3', 'game3_%d.png', 2)
    rf('button', 'button%d.png', 2)
    r('button_back', 'button_back.png')
    r('big_button_back', 'big_button.png')
    rf('letter', 'letter_%d.png', 2)
    r('help-page', 'helppage.png')
    r('escape-page', 'helppage.png')
    r('scores-page', 'scorespage.png')
    r('end-game-page', 'endgamepage.png')
    r('grass', 'grass.png')
    r('sand', 'sand.png')
    r('water', 'water.png')
    r('hole', 'hole.png')
    r('past', 'past.png')    
    r('icon', 'wordgolf.ico')
    
    #
    thegame = game.Game(game.holes[0], 1, 3)
    engine = serge.engine.Engine(title='Word Golf', icon='icon')
    renderer = engine.getRenderer()

    course = serge.render.Layer('course', 0)
    renderer.addLayer(course)
    keys = serge.render.Layer('keys', 1)
    renderer.addLayer(keys)
    ui = serge.render.Layer('ui', 2)
    renderer.addLayer(ui)
    result = serge.render.Layer('results', 3)
    renderer.addLayer(result)

    camera = renderer.getCamera()
    camera.setSpatial(0, 0, 640, 480)



    ### The main world for the game ###

    game_world = serge.world.World('game')
    main = serge.zone.Zone()
    main.active = True
    game_world.addZone(main)

    pad = keypad.KeyPad(game_world, thegame)
    game_world.addActor(pad)

    ### The world for the end of game display ###

    end_world = serge.world.World('end')
    main = serge.zone.Zone()
    main.active = True
    end_world.addZone(main)

    game_over = gameover.Results(thegame, end_world)
    end_world.addActor(game_over)

    ### The world for the start of game display ###

    start_world = serge.world.World('start')
    main = serge.zone.Zone()
    main.active = True
    start_world.addZone(main)
    start = gamestart.Start(thegame, start_world)
    start_world.addActor(start)

    ### The world for help ###

    help_world = serge.world.World('help')
    z = serge.zone.Zone()
    z.active = True
    help_world.addZone(z)
    help = helppage.HelpPage(thegame, help_world)
    help_world.addActor(help)

    ### The world for escape ###

    escape_world = serge.world.World('escape')
    z = serge.zone.Zone()
    z.active = True
    escape_world.addZone(z)
    escape = escapepage.EscapePage(thegame, escape_world)
    escape_world.addActor(escape)

    ### The world for high scores ###

    scores_world = serge.world.World('scores')
    z = serge.zone.Zone()
    z.active = True
    scores_world.addZone(z)
    scores = scorespage.ScoresPage(thegame, scores_world)
    scores_world.addActor(escape)
    scores_world.activateWorld = scores.activateWorld

    # Tell the keypad about the high scores table
    pad.score = scores
    pad.gamestart = start
    scores.gamestart = start
    scores.pad = pad
    scores.updateTable()
    game_over.pad = pad
    game_over.results.visual.pad = pad

    engine.addWorld(start_world)
    engine.addWorld(end_world)
    engine.addWorld(game_world)
    engine.addWorld(help_world)
    engine.addWorld(escape_world)
    engine.addWorld(scores_world)
    engine.setCurrentWorld(start_world)

    thegame.tryHole()

    #serge.builder.builder.main(engine)
    engine.run(options.framerate)
