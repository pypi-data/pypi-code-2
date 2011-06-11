"""This is page for showing help"""

import pygame
import sys

import serge.visual
import serge.actor
import serge.common 
import serge.sound
import serge.blocks.visualblocks
import game 
from theme import get as G



class HelpPage(serge.actor.Actor):
    """Show the help page"""
    
    def __init__(self, game, world):
        """Initialise the page"""
        super(HelpPage, self).__init__('help')
        #
        self.actions = serge.blocks.layout.HorizontalBar('actions', width=400, height=100)
        self.actions.moveTo(320, 450)
        self.actions.setLayerName('ui')
        world.addActor(self.actions)
        #
        b = serge.actor.Actor('button', 'return')
        b.visual = serge.blocks.visualblocks.SpriteText('Return', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleReturn)
        self.actions.addActor(b)
        #
        b = serge.actor.Actor('button', 'quit')
        b.visual = serge.blocks.visualblocks.SpriteText('Quit', G('text-button-colour'), 'button_back', font_size=G('large-text-size'))
        b.linkEvent('left-click', self.handleQuit)
        self.actions.addActor(b)
        #
        self.bg = serge.actor.Actor('help-page')
        self.bg.setSpriteName('help-page')
        self.bg.moveTo(320, 240)
        self.bg.setLayerName('course')
        world.addActor(self.bg)
        #
        self.game = game
        self.world = world


    def handleReturn(self, obj, arg):
        """Handle that we called a restart"""
        serge.sound.Register.playSound('letter')
        self.world.getEngine().setCurrentWorldByName('start')
        
    def handleQuit(self, obj, arg):
        """Handle clicking on quit"""
        self.log.info('Quiting now')
        serge.sound.Register.playSound('end-game')            
        sys.exit(0)
        

