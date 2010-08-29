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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.

'''viewManager.py - defines the ViewManager class which deals with drawing the
state of a universe to the screen.'''

from math import sin, cos

import pygame

from trosnoth.src.utils.utils import timeNow
from trosnoth.src.utils.logging import writeException
from trosnoth.src.trosnothgui.ingame.minimap import MiniMap
from trosnoth.src.gui.framework import framework, elements
from trosnoth.src.trosnothgui.ingame.leaderboard import LeaderBoard
from trosnoth.src.trosnothgui.ingame.statusBar import ZoneProgressBar
from trosnoth.src.trosnothgui.ingame.gameTimer import GameTimer
from trosnoth.src.trosnothgui.ingame.chatBox import ChatBox
from trosnoth.src.trosnothgui.ingame.universegui import UniverseGUI
from trosnoth.src.model.universe_base import GameState

from trosnoth.src.model.map import MapLayout
from trosnoth.src.trosnothgui.ingame.sprites import PlayerSprite

from trosnoth.src.gui.common import Location, FullScreenAttachedPoint

class ViewManager(framework.Element):
    '''A ViewManager object takes a given universe, and displays a screenfull
    of the current state of the universe on the specified screen object.  This
    class displays only a section of the universe and no other information
    (scores, menu etc.).
    
    Note: self._focus represents the position that the ViewManager is currently
    looking at.  self.target is what the ViewManager should be trying to look
    at.
    
    self.target = None - the ViewManager will use its algorithm to follow a
        point of action.
    self.target = (x, y) - the ViewManager will look at the specified point.
    self.target = player - the ViewManager will follow the specified player.
    '''
    
    # The fastest speed that the viewing position can shift in pixels per sec
    maxSpeed = 1800
    acceleration = 1080
    
    # How far ahead of the targeted player we should look.
    lengthFromPlayer = 125
    
    def __init__(self, app, universe, target=None):
        '''Called upon creation of a ViewManager object.  screen is a pygame
        screen object.  universe is the Universe object to draw.  target is
        either a point, a Player object, or None.  If target is None, the view
        manager will follow the action, otherwise it will follow the specified
        point or player.'''
        super(ViewManager, self).__init__(app)
        self.setTarget(target)
        self.universe = universe
        
        # self._focus represents the point where the viewManager is currently
        # looking.
        self._focus = (universe.map.layout.centreX, universe.map.layout.centreY)
        self.lastUpdateTime = timeNow()
        self.speed = 0          # Speed that the focus is moving.
        
        # Create a surface for storing the background stuff.
        self.sRect = None
        self.backdrop = None
        self.spareCanvas = None

        # Now fill the backdrop with what we're looking at now.
        self.appResized()

    def setTarget(self, target):
        '''Makes the viewManager's target the specified value.'''
        self.target = target
        if isinstance(self.target, PlayerSprite):
            # Move directly to looking at player.     
            self._focus = target.pos
            self.reDraw()
        elif isinstance(self.target, (tuple, list)):
            pass
        else:
            self.autoFocusInfo = [0, []]
        
    def getTargetPoint(self):
        '''Returns the position of the current target.'''
        if self.target is None:
            return self._focus
        if isinstance(self.target, PlayerSprite):
            return self.target.pos
        return self.target

    def appResized(self):
        '''
        Called when the app has been resized.
        '''
        self.sRect = sRect = pygame.Rect((0,0), self.app.screenManager.size)
        centre = sRect.center
        sRect.width = min(1024, sRect.width)
        sRect.height = min(768, sRect.height)
        sRect.center = centre

        # Create a surface for storing the background stuff.
        self.backdrop = pygame.surface.Surface(sRect.size).convert()
        self.spareCanvas = pygame.surface.Surface(sRect.size).convert()

        # Now fill the backdrop with what we're looking at now.
        r = pygame.Rect((0, 0), sRect.size)
        self.drawBackdropRect(r)

    def draw(self, screen):
        '''Draws the current state of the universe at the current viewing
        location on the screen.  Does not call pygame.display.flip()'''

        # Update where we're looking at.
        deltaBackdrop = self.updateFocus()
        
        # Create the new backdrop canvas, scrolling the backdrop.
        self.spareCanvas.blit(self.backdrop, deltaBackdrop)
        self.spareCanvas, self.backdrop = self.backdrop, self.spareCanvas
                
        # Fill in the parts which need filling.
        x, y = deltaBackdrop
        yTop = 0
        yHeight = self.sRect.height - abs(y)
        if y > 0:
            # Fill in a gap at the top.
            self.drawBackdropRect(pygame.Rect(0, 0, self.sRect.width, y))
            yTop = y
        elif y < 0:
            # Fill gap at bottom.
            self.drawBackdropRect(pygame.Rect(0, yHeight, self.sRect.width, -y))
        if x > 0:
            # Fill in gap at left.
            self.drawBackdropRect(pygame.Rect(0, yTop, x, yHeight))
        elif x < 0:
            # Fill in gap at right.
            self.drawBackdropRect(pygame.Rect(self.sRect.width + x, yTop, \
                                              -x, yHeight))
        
        # Now put the backdrop onto the screen.
        if self.sRect.topleft != (0, 0):
            screen.fill((0, 0, 0))
        screen.blit(self.backdrop, self.sRect)
        
        # Go through and update the positions of the players on the screen.
        ntGroup = pygame.sprite.Group()
        visPlayers = pygame.sprite.Group()
        for player in self.universe.iterPlayers():
            # Calculate the position of the player.
            player.rect.center = [player.pos[i] - self._focus[i] + \
                    self.sRect.center[i] for i in (0,1)]
        
            # Check if this player needs its nametag shown.
            if player.rect.colliderect(self.sRect):
                visPlayers.add(player)
                player.nametag.rect.midtop = player.rect.midbottom
                # Check that entire nametag's on screen.
                if player.nametag.rect.left < self.sRect.left:
                    player.nametag.rect.left = self.sRect.left
                elif player.nametag.rect.right > self.sRect.right:
                    player.nametag.rect.right = self.sRect.right
                if player.nametag.rect.top < self.sRect.top:
                    player.nametag.rect.top = self.sRect.top
                elif player.nametag.rect.bottom > self.sRect.bottom:
                    player.nametag.rect.bottom = self.sRect.bottom
                ntGroup.add(player.nametag)
                
                # Place the star rectangle below the nametag.
                mx, my = player.nametag.rect.midbottom
                player.starTally.setStars(player.stars)
                player.starTally.rect.midtop = (mx, my-5)
                ntGroup.add(player.starTally)
        
        # Draw the on-screen players and nametags.
        visPlayers.draw(screen)
        ntGroup.draw(screen)
        ntGroup.empty()
        
        # Draw the shots.
        for shot in self.universe.iterShots():
            # Calculate the position of the shot.
            shot.rect.center = [shot.pos[i] - self._focus[i] + \
                    self.sRect.center[i] for i in (0,1)]
            if shot.rect.colliderect(self.sRect):
                screen.blit(shot.image, shot.rect)
        try:
            # Draw the grenades.
            for grenade in self.universe.iterGrenades():
                # Calculate the position of the player.
                grenade.rect.center = [grenade.pos[i] - self._focus[i] + \
                        self.sRect.center[i] for i in (0,1)]
                if grenade.rect.colliderect(self.sRect):
                    screen.blit(grenade.image, grenade.rect)
        except:
            writeException()

    def drawBackdropRect(self, rect):
        '''Updates the contents of the backdrop surface within the specified
        rect. Called when the screen scrolls.'''
        self.backdrop.fill((64, 0, 64), rect)
        
        # Find which map blocks are within the bounds of that rect.
        i, j = MapLayout.getMapBlockIndices(self._focus[0] -
                self.sRect.center[0] + rect.left + self.sRect.left,
                self._focus[1] - self.sRect.center[1] + rect.top +
                self.sRect.top)

        blockRect = pygame.Rect(0, 0, 0, 0)
        
        y = i
        while True:
            if y < 0:
                y += 1
                continue
            try:
                row = self.universe.zoneBlocks[y]
            except IndexError:
                break
            x = j
            first = True
            while True:
                if x < 0:
                    x += 1
                    continue
                try:
                    block = row[x]
                except IndexError:
                    break
                
                # Put the block in its rightful place.
                blockRect.size = block.defn.rect.size
                blockRect.topleft = (
                    block.defn.pos[0] - self._focus[0] + self.sRect.centerx -
                        self.sRect.left,
                    block.defn.pos[1] - self._focus[1] + self.sRect.centery -
                        self.sRect.top
                )

                # Draw the block.
                if blockRect.colliderect(rect):
                    crop = rect.clip(blockRect)
                    self._drawBlock(block, blockRect, crop)
                    x += 1
                    first = False
                else:
                    break
            y += 1
            if first:
                # Not even the first one was drawn; it must have drawn enough
                # rows
                break

    def _drawBlock(self, block, drawRect, area):
        if block.defn.kind in ('top', 'btm'):
            self._drawBodyBlock(block, drawRect, area)
        else:
            self._drawInterfaceBlock(block, drawRect, area)

    def _drawBlockArtwork(self, block, drawRect, area):
        if block.defn.graphics is None:
            return

        # Find its rightful place
        rp = (area.left - drawRect.left, area.top - drawRect.top)
        rr = pygame.rect.Rect(rp, area.size)
        if self.app.displaySettings.showObstacles:
            self.backdrop.blit(block.defn.debugGraphics.graphic, area.topleft,
                    rr)
        else:
            self.backdrop.blit(block.defn.graphics.graphic, area.topleft, rr)

    def _drawBodyBlock(self, block, drawRect, area):
        if block.zone:
            # First draw the background the colour of the zone.
            clr = self._getZoneBackgroundColour(block.zone)
            self.backdrop.fill(clr, area)

            self._drawBlockArtwork(block, drawRect, area)
            
            # Draw the orb.
            img = self._getOrbImage(block.zone)
            r = img.get_rect()
            r.center = block.orbPos(drawRect)
            self.backdrop.blit(img, r)
        else:
            self._drawBlockArtwork(block, drawRect, area)

    def _getOrbImage(self, zone):
        if zone.orbOwner is not None:
            return self.app.theme.sprites.orb(zone.orbOwner)
        else:
            return self.app.theme.sprites.neutralOrb

    def _drawInterfaceBlock(self, block, drawRect, area):
        # First draw the background the colour of the zone.
        if not (block.zone1 or block.zone2):
            # No zones to draw
            return
        
        if (block.zone1 and block.zone2 and block.zone1.zoneOwner == 
                block.zone2.zoneOwner):
            # Same colour; simply fill in that colour
            clr = self._getZoneBackgroundColour(block.zone1)
            self.backdrop.fill(clr, area)
        else:
            if not block.zone1:
                z1 = None
            else:
                if block.zone1.zoneOwner:
                    z1 = block.zone1.zoneOwner.id
                else:
                    z1 = '\x00'
            if not block.zone2:
                z2 = None
            else:
                if block.zone2.zoneOwner:
                    z2 = block.zone2.zoneOwner.id
                else:
                    z2 = '\x00'
                    
            # This is getting a pre-made image for the background colour
            img = self.app.theme.sprites.interfaceBackground(block.defn.kind,
                    z1, z2)

            rp = (area.left - drawRect.left, area.top - drawRect.top)
            rr = pygame.rect.Rect(rp, area.size)
            self.backdrop.blit(img, area.topleft, rr)

        # Now draw the obstacles.
        self._drawBlockArtwork(block, drawRect, area)
                                               
    def updateFocus(self):
        '''Updates the location that the ViewManager is focused on.  First
        calculates where it would ideally be focused, then moves the focus
        towards that point. The focus cannot move faster than self.maxSpeed 
        pix/s, and will only accelerate or decelerate at self.acceleration
        pix/s/s. This method returns the negative of the amount scrolled by.
        This is useful for moving the backdrop by the right amount.
        '''
        
        # Calculate where we should be looking at.
        if isinstance(self.target, PlayerSprite):
            # Take into account where the player's looking.
            plPos = self.target.pos

            if self.app.displaySettings.centreOnPlayer:
                targetPt = plPos
            else:
                radius = self.target.ghostThrust * self.lengthFromPlayer
                #distanceToTarget
                #if radius == None or radius > self.lengthFromPlayer:
                #    radius = self.lengthFromPlayer
                    
                plAngle = self.target.angleFacing
                targetPt = (plPos[0] + radius * sin(plAngle),
                            plPos[1] - radius * cos(plAngle))

            # If the player no longer exists, look wherever we want.
            if not self.universe.hasPlayer(self.target):
                self.setTarget(None)
        elif isinstance(self.target, (tuple, list)):
            targetPt = self.target
        else:
            # Follow the action.
            countdown, players = self.autoFocusInfo

            # First check for non-existent players.
            for p in players:
                if not self.universe.hasPlayer(p):
                    players.remove(p)

            if self.universe.getPlayerCount() == 0:
                # No players anywhere. No change.
                targetPt = tuple(self._focus)
            elif len(players) == 0:
                # No players in view. Look for action.
                # Less than 4 players. Look for more action.
                maxP = 0
                curZone = None
                for z in self.universe.zones:
                    count = len(self.universe.getPlayersInZone(z))
                    if count > maxP:
                        maxP = count
                        curZone = z
                self.autoFocusInfo[1] = self.universe.getPlayersInZone(curZone)

                targetPt = tuple(self._focus)
                countdown = 10
            else:
                # Look at centre-of-range of these players.
                minPos = [min(p.pos[i] for p in players) for i in (0,1)]
                maxPos = [max(p.pos[i] for p in players) for i in (0,1)]
                targetPt = [0.5 * (minPos[i] + maxPos[i]) for i in (0,1)]

                # Every 10 iterations recheck details.
                if countdown <= 0:
                    # Count players in view.
                    numInView = 0
                    for p in self.universe.iterPlayers():
                        if abs(p.pos[0] - targetPt[0]) < self.app.screenManager.scaledSize[0] and \
                                abs(p.pos[1] - targetPt[1]) < self.app.screenManager.scaledSize[1]:
                            numInView += 1

                    if numInView < 4:
                        # Less than 4 players. Look for more action.
                        maxP = 0
                        curZone = None
                        for z in self.universe.zones:
                            count = len(self.universe.getPlayersInZone(z))
                            if count > maxP:
                                maxP = count
                                curZone = z
                        self.autoFocusInfo[1] = self.universe.getPlayersInZone(curZone)
                    countdown = 10
                countdown -= 1
        
        # Calculate time that's passed.
        now = timeNow()
        deltaT = now - self.lastUpdateTime
        self.lastUpdateTime = now
        
        # Calculate distance to target.
        sTarget = sum((targetPt[i] - self._focus[i])**2 for i in (0,1)) ** 0.5
        
        if sTarget == 0:
            return (0, 0)
        
        # If smooth panning is switched off, jump to location.
        if not self.app.displaySettings.smoothPanning:
            s = sTarget
        else:
            # Calculate the maximum velocity that will result in deceleration to
            # reach target. This is based on v**2 = u**2 + 2as
            vDecel = (2. * self.acceleration * sTarget) ** 0.5
            
            # Actual velocity is limited by this and maximum velocity.
            self.speed = min(self.maxSpeed, vDecel, \
                             self.speed + self.acceleration * deltaT)
            
            # Distance travelled should never overshoot the target.
            s = min(sTarget, self.speed * deltaT)
        
        # How far does the backdrop need to move by?
        #  (This will be negative what the focus moves by.)
        deltaBackdrop = tuple(round(-s * (targetPt[i] - self._focus[i]) \
                                    / sTarget, 0) for i in (0,1))
        
        # Calculate the new focus.
        self._focus = tuple(round(self._focus[i] - deltaBackdrop[i], 0) \
                            for i in (0,1))
        
        # Return the distance the backdrop must be moved.
        return deltaBackdrop

    def reDraw(self):
        r = pygame.Rect((0, 0), self.sRect.size)
        self.drawBackdropRect(r)

    def _getZoneBackgroundColour(self, zone):
        colours = self.app.theme.colours
        if zone.zoneOwner:
            return colours.backgroundColour(zone.zoneOwner)
        else:
            return colours.neutral_bg

class PregameMessage(elements.TextElement):
    def __init__(self, app, pos=None):
        if pos is None:
            pos = Location(FullScreenAttachedPoint((0, -150), 'center'), 'center')
        super(PregameMessage, self).__init__(
            app,
            '',
            app.screenManager.fonts.bigMenuFont,
            pos,
            app.theme.colours.pregameMessageColour,
            shadow = True
        )
        self.setShadowColour((0,0,0))

class GameViewer(framework.CompoundElement):
    '''The gameviewer comprises a viewmanager and a minimap, which can be
    switched on or off.'''

    zoneBarHeight = 25

    def __init__(self, app, gameInterface, world):
        super(GameViewer, self).__init__(app)
        self.interface = gameInterface
        self.world = world
        self.worldgui = UniverseGUI(app, self.world)
        self.app = app

        self.viewManager = ViewManager(self.app, self.worldgui)

        self.timerBar = GameTimer(app, world)
        self.chatBox = ChatBox(self.app, self.world, self)
        self.miniMap = None
        self.pregameMessage = None
        self.leaderboard = None
        self.zoneBar = None
        self.makeMiniMap()

        self.elements = [self.viewManager, self.pregameMessage]
        self._screenSize = tuple(app.screenManager.size)

        self.minimapDisruptor = None
        self.teamsDisrupted = set()

        self.toggleInterface()
        self.toggleLeaderBoard()

    def resizeIfNeeded(self):
        '''
        Checks whether the application has resized and adjusts accordingly.
        '''
        if self._screenSize == self.app.screenManager.size:
            return
        self._screenSize = tuple(self.app.screenManager.size)

        self.viewManager.appResized()
        # Recreate the minimap.
        showHUD = self.miniMap in self.elements
        showLeader = self.leaderboard in self.elements
        self.makeMiniMap()
        if showHUD:
            self.toggleInterface()
        if showLeader:
            self.toggleLeaderBoard()
            

    def makeMiniMap(self):
        self.miniMap = MiniMap(self.app, 20, self.world, self.viewManager)
        xPos = -10
        yPos = self.miniMap.getRect().bottom + self.zoneBarHeight - 5
        messagePos = Location(FullScreenAttachedPoint((xPos, yPos), 'topright'), 'topright')
        self.pregameMessage = PregameMessage(self.app, messagePos)
        self.zoneBar = ZoneProgressBar(self.app, self.world, self)
        self.leaderboard = LeaderBoard(self.app, self.world, self)

        self.elements = [self.viewManager, self.pregameMessage]

    def updatePregameMessage(self):
        text = ''
        if self.world.gameState == GameState.InProgress:
            text = ''
        elif self.world.gameState == GameState.PreGame:
            text = 'Game will begin when both captains signal ready.'
        elif self.world.gameState == GameState.Starting:
            text = 'Prepare yourself...'
        else:
            pi = self.interface.runningPlayerInterface
            if pi is not None and pi.player is not None:
                team = pi.player.team
                if team is self.world.winningTeam:
                    text = 'Congratulations!'
                else:
                    text = 'Better luck next time!'
            else:
                text = 'Game is over!'
        self.pregameMessage.setText(text)
                
    def setTarget(self, target):
        'Target should be a player, a point, or None.'
        self.viewManager.setTarget(target)
        if isinstance(target, PlayerSprite):
            if target.team in self.teamsDisrupted:
                self.miniMap.disrupted()
            else:
                self.miniMap.endDisruption()
        
    def tick(self, deltaT):
        self.resizeIfNeeded()
        self.worldgui.tick(deltaT)
        self.updatePregameMessage()
        super(GameViewer, self).tick(deltaT)

    def minimapDisruption(self, player):
        disruptedTeam = player.team.opposingTeam
        self.teamsDisrupted.add(disruptedTeam)
        if isinstance(self.viewManager.target, PlayerSprite):
            if self.viewManager.target.team == disruptedTeam:
                self.miniMap.disrupted()
                self.zoneBar.disrupt = True
                self.minimapDisruptor = player

    def endMinimapDisruption(self, player):
        disruptedTeam = player.team.opposingTeam
        self.teamsDisrupted.remove(disruptedTeam)
        if self.viewManager.target.team == disruptedTeam:
            self.minimapDisruptor = None
            self.miniMap.endDisruption()
            self.zoneBar.disrupt = False

    def toggleInterface(self):
        if self.miniMap in self.elements:
            self.elements.remove(self.zoneBar)
            self.elements.remove(self.timerBar)
            self.elements.remove(self.miniMap)
        else:
            self.elements.append(self.zoneBar)
            self.elements.append(self.timerBar)
            self.elements.append(self.miniMap)
            self.timerBar.syncTimer()

    def toggleLeaderBoard(self):
        if self.leaderboard in self.elements:
            self.elements.remove(self.leaderboard)
        else:
            self.elements.append(self.leaderboard)

    def openChat(self, player):
        self.chatBox.reset()
        self.chatBox.setPlayer(player)
        self.chatBox.Show()

    def closeChat(self):
        self.chatBox.Close()
        
