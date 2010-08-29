# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009  Joshua Bartlett
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import pygame

from trosnoth.src.gui.framework.elements import TextElement
from trosnoth.src.gui.framework import clock, timer
from trosnoth.src.gui.common import (Area, FullScreenAttachedPoint, Location,
        ScaledSize)
import trosnoth.src.gui.framework.framework as framework
from trosnoth.src.model.universe_base import GameState
from trosnoth.src.utils import logging
from twisted.internet import task, reactor

class GameTimer(framework.CompoundElement):
    def __init__(self, app, world):
        super(GameTimer, self).__init__(app)
        self.world = world
        self.app = app

        # Change these constants to say where the box goes
        self.area = Area(FullScreenAttachedPoint(ScaledSize(0, -3), 'midtop'), ScaledSize(110, 35), 'midtop')

        self.lineWidth = max(int(3*self.app.screenManager.scaleFactor), 1)
        # Anything more than width 2 looks way too thick
        if self.lineWidth > 2:
            self.lineWidth = 2
        self.notStarted = TextElement(self.app, "xx:xx",
                                      self.app.screenManager.fonts.timerFont,
                                      Location(FullScreenAttachedPoint(ScaledSize(0, -2), 'midtop'), 'midtop'),
                                      app.theme.colours.timerFontColour)
        self.elements = [self.notStarted]
        self.running = False

        self.flashControl = task.LoopingCall(self.flash)
    
        self.gameTimer = None
        self.timerAdjustLoop = None
        self.countingDown = None
        self.startedFlashing = False

        # Seconds between alternating flashes
        self.flashFreq = 0.25
        # Value the countdown has to get to before it starts to flash
        self.flashValue = 30

        self.flashState = 0
        self.loop()

    def loop(self):
        self.timerAdjustLoop = reactor.callLater(10, self.loop)
        self.syncTimer()

    def checkState(self):
        if self.world.gameState != GameState.InProgress:
            if self.running:
                self.gameFinished()
        elif not self.running:
            self.gameStarted(self.world.getTimeLeft())

    def syncTimer(self):
        self.checkState()
        if self.gameTimer is None:
            return
        time = self.world.getTimeLeft()
        
        if time < 0:
            self.gameTimer.counted = -time
        else:
            self.gameTimer.countTo = time
            self.gameTimer.counted = 0

    def flash(self):
        try:
            self._flash()
        except:
            print 'UNHANDLED ERROR IN GameTimer.flash()'
            print
            logging.writeException()

    def _flash(self):
        if not self.countingDown:
            return
        
        if not self.startedFlashing:
            if self.gameTimer.getCurTime() <= self.flashValue:
                self.startedFlashing = True
            else:
                return

        if self.flashState == 0:
            self.gameClock.setColours(self.app.theme.colours.timerFlashColour)
            self.flashState = 1
        else:
            self.gameClock.setColours(self.app.theme.colours.timerFontColour)
            self.flashState = 0

    def kill(self):
        if self.world.gameState == GameState.InProgress and self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
        self.gameTimer = None
        
        if self.flashControl.running:
            self.flashControl.stop()

    def gameStarted(self, time):
        self.running = True

        if time > 0:
            self.gameTimer = timer.CountdownTimer(time, highest = "minutes")
            self.countingDown = True
        else:
            self.gameTimer = timer.Timer(startAt = -time, highest = "minutes")
            self.countingDown = False
            
        self.gameClock = clock.Clock(self.app, self.gameTimer,
                                     Location(FullScreenAttachedPoint(ScaledSize(0, -2), 'midtop'), 'midtop'),
                                     self.app.screenManager.fonts.timerFont,
                                     self.app.theme.colours.timerFontColour)
        self.gameTimer.start()
        self.elements = [self.gameClock]

        self.flashControl.start(self.flashFreq)

    def gameFinished(self):
        self.running = False
        if self.timerAdjustLoop is not None:
            self.timerAdjustLoop.cancel()
            self.timerAdjustLoop = None
            self.gameTimer.pause()
            self.flashControl.stop()
            self.gameClock.setColours(self.app.theme.colours.timerFontColour)
            self.gameTimer = None
        self.elements = [self.notStarted]

    def _getRect(self):
        return self.area.getRect(self.app)


    def draw(self, surface):     
        self.checkState()
        timerBox = self._getRect()
        # Box background
        surface.fill(self.app.theme.colours.timerBackground, timerBox)
        pygame.draw.rect(surface, self.app.theme.colours.black, timerBox,
                self.lineWidth)   # Box border
        
        super(GameTimer, self).draw(surface)

