# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2009 Joshua D Bartlett
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
# Foundation, Inc., 51 Franklin  Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

import pygame

from pygame.locals import QUIT

from screenManager import screenManager, windowManager
from trosnoth.src.gui.sound.musicManager import MusicManager
from trosnoth.src.gui.sound.soundPlayer import SoundPlayer
from trosnoth.src.utils import logging
from trosnoth.src.utils.utils import timeNow, RunningAverage

class ApplicationExit(Exception):
    pass

class Application(object):
    '''Instantiating the Main class will set up a ui. Calling the run()
    method will run the application.'''

    def __init__(self, size, graphicsOptions, caption, element):
        '''Initialise the application.'''
        self._options = (element, size, graphicsOptions, caption)
        self._initSound()
        self._makeScreenManager(element, size, graphicsOptions, caption)
        self.fonts = self.screenManager.fonts
        self.initialise()
        self.screenManager.createInterface(element)
        self._running = False
        self.lastTime = None
        self.tickRate = RunningAverage(500)
        self.tickTime = RunningAverage(500)
        self.drawTime = RunningAverage(500)
        self.flipTime = RunningAverage(500)

    def __getattr__(self, attr):
        if attr == 'interface':
            return self.screenManager.interface
        raise AttributeError

    def _initSound(self):
        self.musicManager = MusicManager()
        self.soundPlayer = SoundPlayer()

    def _makeScreenManager(self, element, size, graphicsOptions, caption):
        self.screenManager = screenManager.ScreenManager(self, size,
                                                         graphicsOptions, caption)

    def restart(self):
        self._initSound()
        self._makeScreenManager(*self._options)
        self.fonts = self.screenManager.fonts
        self.initialise()
        self.screenManager.createInterface(self._options[0])

    def initialise(self):
        '''
        Provides the opportunity for initialisation by subclasses before the
        interface element is created.
        '''

    def getFontFilename(self, fontName):
        '''
        May be overridden by an application in order to provide a custom font
        location, or some other mapping from font name to filename.
        '''
        return fontName

    def run(self):
        '''Runs the application.'''
        def _stop():
            self._running = False
            raise ApplicationExit
        self._stop = _stop
        
        self._running = True
        self.lastTime = timeNow()
        while self._running:
            try:
                self.tick()
            except ApplicationExit:
                break
        pygame.quit()

    def run_twisted(self, reactor=None):
        '''Runs the application using Twisted's reactor.'''
        from twisted.internet import task

        if reactor is None:
            from twisted.internet import reactor
        
        def _stop():
            if not self._running:
                print 'stop() called twice. Terminating immediately.'
                reactor.stop()
                return

            self._running = False

            # Give time for shutdown sequence.
            reactor.callLater(0.3, reactor.stop)

        self._stop = _stop
        self.lastTime = timeNow()
        
        task.LoopingCall(self.tick).start(0.02, False)
        self._running = True
        reactor.run()
        pygame.quit()

    def stop(self):
        if self._running:
            self.stopping()
        self._stop()
        
    def tick(self):
        try:
            self._tick()
        except ApplicationExit:
            raise
        except:
            logging.writeException()

    def _tick(self):
        '''Processes the events in the pygame event queue, and causes the
        application to be updated, then refreshes the screen. This routine is
        called as often as possible - it is not limited to a specific frame
        rate.'''
        if not self._running:
            return

        # Process the events in the event queue.
        for event in pygame.event.get():
            try:
                event = self.musicManager.processEvent(event)
                if not self._running:
                    return
                if event is not None:
                    event = self.screenManager.processEvent(event)
                    if not self._running:
                        return
                    if event is not None:
                        # Special events.
                        if event.type == QUIT:
                            self.stop()
                            return
            except ApplicationExit:
                raise
            except:
                logging.writeException()
            if not self._running:
                return

        # Give things an opportunity to update their state.
        now = timeNow()
        deltaT = now - self.lastTime
        self.tickRate.noteValue(deltaT)
        self.lastTime = now
        try:
            self.screenManager.tick(deltaT)
        except ApplicationExit:
            raise
        except:
            print "UNHANDLED ERROR IN TICK"
            print
            logging.writeException()
        t0 = timeNow()
        self.tickTime.noteValue(t0 - self.lastTime)
            
        if not self._running:
            return

        if pygame.display.get_active():
            # Update the screen.
            try:
                self.screenManager.draw(self.screenManager.screen)
            except pygame.error, E:
                # Surface may have been lost (DirectDraw error)
                print 'Pygame error: %s' % (E,)
    
            # Flip the display.
            t1 = timeNow()
            self.drawTime.noteValue(t1 - t0)
            pygame.display.flip()
            self.flipTime.noteValue(timeNow() - t1)

    def stopping(self):
        '''Any finalisation which must happen before stopping the reactor.'''
        self.screenManager.finalise()


class MultiWindowApplication(Application):

    def _makeScreenManager(self, element, size, graphicsOptions, caption):
        self.screenManager = windowManager.WindowManager(self, element, size,
                                                         graphicsOptions, caption)
