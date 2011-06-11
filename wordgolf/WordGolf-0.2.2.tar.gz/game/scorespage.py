"""This is page for showing the high scores"""

import pygame
import sys
import os

import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.visualblocks
import serge.blocks.scores
import game 
import common
from theme import get as G


### The high score table ###


class ScoresPage(serge.actor.Actor, common.MoveableBackground):
    """Show the scores page"""
    
    def __init__(self, game, world):
        """Initialise the page"""
        super(ScoresPage, self).__init__('scores')
        #
        self.addLogo(world)
        #
        self.actions = serge.blocks.layout.HorizontalBar('actions', height=100)
        self.actions.moveTo(320, 400)
        self.actions.setLayerName('ui')
        world.addActor(self.actions)
        #
        #b = serge.actor.Actor('button', 'return')
        #b.visual = serge.blocks.visualblocks.SpriteText('Return', BUTTON_TEXT, 'button_back', font_size=BIG_TEXT)
        #b.linkEvent('left-click', self.handleReturn)
        #self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'play')
        b.visual = serge.blocks.visualblocks.SpriteText('Play', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handlePlay)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'reset')
        b.visual = serge.blocks.visualblocks.SpriteText('Reset', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleReset)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'quit')
        b.visual = serge.blocks.visualblocks.SpriteText('Quit', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleQuit)
        self.actions.addActor(b)
        #
        self.background = serge.actor.Actor('scores-page')
        self.background.setSpriteName('scores-page')
        self.background.moveTo(320, 240)
        self.background.setLayerName('course')
        world.addActor(self.background)
        #
        # The scores
        self.shots = serge.blocks.layout.VerticalBar('ui-grid', width=G('score-grid-width'), height=G('score-grid-height'))
        self.shots.setOrigin(G('score-grid-offset-x'), G('score-grid-offset-y'))
        self.shots.setLayerName('ui')
        t = serge.actor.Actor('text', 'header')
        t.visual = serge.visual.Text('', G('text-button-colour'), font_size=G('normal-text-size'), justify='left')
        self.shots.addActor(t)
        #
        self.shots_row = []
        for row in range(5):
            t = serge.actor.Actor('text', row)
            t.visual = serge.visual.Text('', G('text-button-colour'), font_size=G('large-text-size'), justify='left')
            self.shots.addActor(t)
            self.shots_row.append(t)
        world.addActor(self.shots)

        #
        self.game = game
        self.world = world
        #
        self.setUpTable()
        self.game_start = None
        #
        self.addEffects()
        
    def setUpTable(self):
        """Set up the high score table"""
        var = 'HOME' if not sys.platform.startswith('win') else 'HOMEPATH'
        self.score_filename = os.path.join(os.getenv(var), '.bogolf.scores')
        if os.path.isfile(self.score_filename):
            self.log.info('Loading scores from %s' % self.score_filename)
            self.table = serge.serialize.Serializable.fromFile(self.score_filename)
        else:
            self.log.info('New scores file at %s' % self.score_filename)
            self.resetTable()

    def saveTable(self):
        """Save the high score table"""
        self.table.toFile(self.score_filename)

    def handleReturn(self, obj, arg):
        """Handle that we requested to return"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('end')

    def handlePlay(self, obj, arg):
        """Handle that we requested to play"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('start')
        
    def handleQuit(self, obj, arg):
        """Handle clicking on quit"""
        self.log.info('Quiting now')
        serge.sound.Register.playSound('end-game')            
        sys.exit(0)
        
    def handleReset(self, obj, arg):
        """Handle clicking on reset"""
        self.log.info('Resetting high scores')
        serge.sound.Register.playSound('letter')         
        self.table.resetCategory('%s - %d holes - shots' % (self.gamestart.selected_game_name, self.gamestart.selected_holes))
        self.updateTable()
                
    def resetTable(self):
        """Reset the scores table"""   
        self.table = serge.blocks.scores.HighScoreTable()
        for game in (('easy', 'medium', 'hard')):
            for holes in (1, 3, 6, 9, 12, 15, 18):
                self.table.addCategory('%s - %d holes - shots' % (game, holes), 
                        number=5, sort_columns=[1,2], directions=['descending', 'descending'])
                self.table.addCategory('%s - %d holes - time' % (game, holes), 
                        number=5, sort_columns=[2,1], directions=['descending', 'descending'])
        self.saveTable()
        
    def activateWorld(self):
        """When we are activated"""
        if self.gamestart:
            self.updateTable()
               
    def updateTable(self):
        """Update the current scores table"""
        for row in range(5):
            self.shots_row[row].setText('')
        results = self.table.getCategory('%s - %d holes - shots' % (self.gamestart.selected_game_name, self.gamestart.selected_holes))
        for row, (name, shots, time, date) in enumerate(results):
            if shots == 0:
                result = 'Even par'
            else:
                result = '%d %s par' % (abs(shots), 'over' if shots > 0 else 'under')
            if self.pad.this_score == row+1:
                self.shots_row[row].visual.setColour((255,255,255))
            else:    
                self.shots_row[row].visual.setColour(G('text-button-colour'))
            self.shots_row[row].setText('%d - %s in %s seconds' % (row+1, result, self.niceTime(time)))
            
            
