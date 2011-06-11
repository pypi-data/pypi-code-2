import pygame
import sys


import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.visualblocks
import serge.blocks.layout
import serge.engine
import game 
import common
from theme import get as G



class Start(serge.actor.Actor, common.MoveableBackground):
    """Show the start menu"""
    
    possible_holes = [1, 3, 6, 9, 12, 18]
    
    def __init__(self, game, world):
        """Initialise the start menu"""
        super(Start, self).__init__('start')
        self.allow_continue = False
        #
        self.addLogo(world)
        #
        self.background = serge.actor.Actor('bg')
        self.background.setSpriteName('start-bg')
        self.background.moveTo(320, 240)
        self.background.setLayerName('course')
        world.addActor(self.background)
        #
        # Buttons for the different number of holes
        self.holes, self.selected_holes = {}, None
        self.holes_bar = serge.blocks.layout.HorizontalBar('bar', height=100)
        self.holes_bar.setOrigin(0, 80)
        self.holes_bar.setLayerName('ui')
        world.addActor(self.holes_bar)
        #
        for i, holes in enumerate(self.possible_holes):
            h = serge.actor.Actor('hole-button', 'h%d' % holes)
            h.resizeTo(G('hole-button-width'), G('hole-button-height'))
            h.visual = serge.blocks.visualblocks.TextToggle(
                ('%d holes' % holes), G('text-button-colour'), 'button', font_size=G('hole-button-font-size'))
            h.visual.setOff()
            h.linkEvent('left-click', self.handleButton, holes)
            self.holes[holes] = h
            self.holes_bar.addActor(h)
        #
        # Buttons for the different games
        self.games, self.selected_game = {}, None
        self.games_bar = serge.blocks.layout.Grid('bar', size=(3,2), height=130)
        self.games_bar.setOrigin(0, 200)
        self.games_bar.setLayerName('ui')
        world.addActor(self.games_bar)
        #
        for i, name in enumerate(('Easy', 'Medium', 'Hard')):
            g = serge.actor.Actor('game-button', 'g%d' % (i+1))
            g.resizeTo(G('game-button-width'), G('game-button-height'))
            g.visual = serge.blocks.visualblocks.Toggle(('game%d' % (i+1)))
            g.visual.setOff()
            g.linkEvent('left-click', self.handleGame, (i+1))
            self.games[i+1] = g
            self.games_bar.addActor((i,0), g)
            #
            t = serge.actor.Actor('text', name)
            t.visual = serge.visual.Text(name, G('text-button-colour'), font_size=G('large-text-size'))
            self.games_bar.addActor((i,1), t)
        #
        self.actions1 = serge.blocks.layout.HorizontalBar('actions1', height=100)
        self.actions1.moveTo(320, 360)
        self.actions1.setLayerName('ui')
        world.addActor(self.actions1)
        #
        b = serge.actor.Actor('button', 'start')
        b.visual = serge.blocks.visualblocks.SpriteText('Start', G('text-button-colour'), 'big_button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleStart)
        self.actions1.addActor(b)
        #
        self.actions2 = serge.blocks.layout.HorizontalBar('actions2', height=100)
        self.actions2.moveTo(320, 430)
        self.actions2.setLayerName('ui')
        world.addActor(self.actions2)
        #
        b = serge.actor.Actor('button', 'scores')
        b.visual = serge.blocks.visualblocks.SpriteText('Scores', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleScores)
        self.actions2.addActor(b)
        #
        b = serge.actor.Actor('button', 'help')
        b.visual = serge.blocks.visualblocks.SpriteText('Help', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleHelp)
        self.actions2.addActor(b)
        #
        b = serge.actor.Actor('button', 'quit')
        b.visual = serge.blocks.visualblocks.SpriteText('Quit', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleQuit)
        self.actions2.addActor(b)
        #
        self.version = serge.actor.Actor('text', 'version')
        self.version.visual = serge.visual.Text('v'+common.version, G('text-button-colour'), font_size=8, justify='left')
        self.version.setLayerName('ui')
        self.version.setOrigin(600, 460)
        world.addActor(self.version)
        #
        self.game = game
        self.world = world
        #
        self.selectHoles(3)
        self.selectGame(1)
        #
        self.addEffects()
        
        
    def selectHoles(self, holes):
        """Select the certain number of holes"""
        if self.selected_holes:
            self.holes[self.selected_holes].visual.setOff()
        self.selected_holes = holes
        self.holes[self.selected_holes].visual.setOn()

    def selectGame(self, game):
        """Select the certain game"""
        if self.selected_game:
            self.games[self.selected_game].visual.setOff()
        self.selected_game = game
        self.selected_game_name = ['easy', 'medium', 'hard'][game-1]
        self.games[self.selected_game].visual.setOn()

    def handleButton(self, obj, holes):
        """Handle the user selecting the number of buttons"""
        self.log.info('Selected number of holes %d' % holes)
        self.selectHoles(holes)
        serge.sound.Register.playSound('letter')
        
    def handleStart(self, obj, arg):
        """Handle the user clicking on the start button"""
        self.world.getEngine().setCurrentWorldByName('game')
        self.world.getEngine().getCurrentWorld().findActorByName('keypad').restartGame(self.selected_holes, self.selected_game)
        serge.sound.Register.playSound('begin')

    def handleGame(self, obj, game):
        """Handle that the user selected a game"""
        self.log.info('Selected game %d' % game)
        self.selectGame(game)
        serge.sound.Register.playSound('letter')            

    def handleHelp(self, obj, arg):
        """Handle clicking on help"""
        self.log.info('Go to help')
        serge.sound.Register.playSound('letter')            
        self.world.getEngine().setCurrentWorldByName('help')

    def handleScores(self, obj, arg):
        """Handle clicking on scores"""
        self.log.info('Go to scores')
        serge.sound.Register.playSound('letter')            
        self.world.getEngine().setCurrentWorldByName('scores')

    def handleQuit(self, obj, arg):
        """Handle clicking on quit"""
        self.log.info('Quiting now')
        serge.sound.Register.playSound('end-game')            
        sys.exit(0)
        

