"""This is the display when the game is over"""

import pygame
import sys

import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.visualblocks
import game 
import common
from theme import get as G



class Results(serge.actor.Actor, common.MoveableBackground):
    """Show the results"""
    
    def __init__(self, game, world):
        """Initialise the results"""
        super(Results, self).__init__('results')
        self.results = serge.actor.Actor('results')
        self.results.visual = ResultList()
        self.results.setLayerName('results')
        self.results.setSpatial(G('final-offset-x'), G('final-offset-y'), 0, 0)
        world.addActor(self.results)
        #
        self.congrats = serge.actor.Actor('text')
        self.congrats.visual = serge.visual.Text('', G('congrats-text-colour'), font_size=G('final-text-size'), justify='left')
        self.congrats.setOrigin(G('final-offset-x'), G('congrats-offset-y'))
        self.congrats.setLayerName('ui')
        world.addActor(self.congrats)
        #
        self.actions = serge.blocks.layout.HorizontalBar('actions', width=400, height=100)
        self.actions.moveTo(320, 400)
        self.actions.setLayerName('ui')
        world.addActor(self.actions)
        #
        b = serge.actor.Actor('button', 'start')
        b.visual = serge.blocks.visualblocks.SpriteText('Play', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleRestart)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'scores')
        b.visual = serge.blocks.visualblocks.SpriteText('Scores', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleScores)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'quit')
        b.visual = serge.blocks.visualblocks.SpriteText('Quit', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleQuit)
        self.actions.addActor(b)
        #
        self.background = serge.actor.Actor('end-game')
        self.background.setSpriteName('end-game-page')
        self.background.moveTo(320, 240)
        self.background.setLayerName('course')
        world.addActor(self.background)
        #
        self.game = game
        self.world = world
        #
        self.addEffects()


    def handleRestart(self, obj, arg):
        """Handle that we called a restart"""
        serge.sound.Register.playSound('start')
        self.world.getEngine().setCurrentWorldByName('start')

    def handleScores(self, obj, arg):
        """Handle that we asked to see the high scores"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('scores')
        
    def updateActor(self, interval, world):
        """Update the world"""
        game = self.world.getEngine().getWorld('game').findActorByName('keypad').game
        if game.isEnded():
            self.results.visual.results = ['You scored %s in %s seconds' % 
                (game.getScoreText(), self.niceTime(self.pad.clock)), ''] + game.getResults()
            if self.pad.this_score is None:
                self.congrats.setText('')
            else:
                self.congrats.setText('You were %d on the high score table' % self.pad.this_score)

    def handleQuit(self, obj, arg):
        """Handle clicking on quit"""
        self.log.info('Quiting now')
        serge.sound.Register.playSound('end-game')            
        sys.exit(0)
        

           
class ResultList(serge.visual.Drawing):
    """Show results for holes"""
    
    def __init__(self):
        """Initialise the list"""
        super(ResultList, self).__init__()
        self.results = []
        self.text = serge.visual.Text('', G('final-text-colour'), font_size=G('large-text-size'))
        
    def renderTo(self, milliseconds, surface, (x, y)):
        """Render to a surface"""
        self.text.setFontSize({12:G('large-text-size')*2/3, 15:G('large-text-size')*2/3, 18:G('large-text-size')/3}.get(len(self.results), G('large-text-size')))
        for i, row in enumerate(self.results):  
            self.text.setText(row)      
            self.text.renderTo(milliseconds, surface, (x, y+i*G('final-line-offset')))
            
            

            

