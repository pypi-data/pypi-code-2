"""This is page for showing when user presses escape"""

import pygame
import sys

import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.visualblocks
import game 
from theme import get as G



class EscapePage(serge.actor.Actor):
    """Show the escape page"""
    
    def __init__(self, game, world):
        """Initialise the page"""
        super(EscapePage, self).__init__('escape')
        #
        self.actions = serge.blocks.layout.HorizontalBar('actions', width=400, height=100)
        self.actions.moveTo(G('escape-offset-x'), G('escape-offset-y'))
        self.actions.setLayerName('ui')
        world.addActor(self.actions)
        #
        b = serge.actor.Actor('button', 'return')
        b.visual = serge.blocks.visualblocks.SpriteText('Return', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleReturn)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'restart')
        b.visual = serge.blocks.visualblocks.SpriteText('Restart', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleRestart)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'quit')
        b.visual = serge.blocks.visualblocks.SpriteText('Quit', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleQuit)
        self.actions.addActor(b)
        #
        self.bg = serge.actor.Actor('escape-page')
        self.bg.setSpriteName('escape-page')
        self.bg.moveTo(320, 240)
        self.bg.setLayerName('course')
        world.addActor(self.bg)
        #
        self.game = game
        self.world = world


    def handleReturn(self, obj, arg):
        """Handle that we called a return"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('game')

    def handleRestart(self, obj, arg):
        """Handle that we called for a restart"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('start')
        
    def handleQuit(self, obj, arg):
        """Handle clicking on quit"""
        self.log.info('Quiting now')
        serge.sound.Register.playSound('end-game')            
        sys.exit(0)
        

