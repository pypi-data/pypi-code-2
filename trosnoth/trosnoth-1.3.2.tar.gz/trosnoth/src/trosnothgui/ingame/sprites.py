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

import pygame
from trosnoth.src.gui.framework.basics import AngledImageCollection, Animation
from trosnoth.src.trosnothgui import defines
from trosnoth.src.trosnothgui.ingame.nametag import NameTag, StarTally

from trosnoth.src.model.obstacles import VerticalWall
import random


class ShotSprite(pygame.sprite.Sprite):
    def __init__(self, app, shot):
        super(ShotSprite, self).__init__()
        self.app = app
        self.shot = shot
        self.shotAnimation = app.theme.sprites.shotAnimation(shot.team)
        # Need a starting one:
        self.image = self.shotAnimation.getImage()
        self.rect = self.image.get_rect()

    def update(self):
        self.image = self.shotAnimation.getImage()

            

    @property
    def pos(self):
        return self.shot.pos

class GrenadeSprite(pygame.sprite.Sprite):
    def __init__(self, app, grenade):
        super(GrenadeSprite, self).__init__()
        self.grenade = grenade
        self.image = app.theme.sprites.grenade
        self.rect = self.image.get_rect()
        
    @property
    def pos(self):
        return self.grenade.pos

class PlayerSprite(pygame.sprite.Sprite):
    # These parameters are used to create a canvas for the player sprite object.
    canvasSize = (33, 39)
    colourKey = (255, 255, 255)
    def __init__(self, app, player):
        super(PlayerSprite, self).__init__()
        self.app = app
        self.player = player
        self.nametag = NameTag(app, player.nick)
        self.starTally = StarTally(app, 0)

        sprites = app.theme.sprites
        gunImages = AngledImageCollection(self.getAngleFacing,
                *sprites.gunImages(self.player.team))

        self.runningAnimation = [
                Animation(0.1, *sprites.runningLegs),
                sprites.playerHead,
                sprites.playerBody,
                gunImages,
                sprites.playerTeam(self.player.team),
        ]
        
        self.reversingAnimation = [
            gunImages,
            sprites.playerBody,
            sprites.playerHead,
            Animation(0.2, *sprites.backwardsLegs),
            sprites.playerTeam(self.player.team),
        ]

        self.turretAnimation = [
            sprites.turretBase,
            sprites.playerBody,
            sprites.playerHead,
            sprites.playerTeam(self.player.team),
            gunImages,
        ]

        self.standingAnimation = [
            sprites.playerStanding,
            sprites.playerBody,
            gunImages,
            sprites.playerHead,
            sprites.playerTeam(self.player.team),
        ]

        self.jumpingAnimation = [
            sprites.playerHead,
            sprites.playerJumping,
            gunImages,
            sprites.playerBody,
            sprites.playerTeam(self.player.team),
        ]
        self.holdingAnimation = [
            sprites.playerHead,
            sprites.playerBody,
            sprites.playerHolding(self.player.team),
            sprites.playerTeam(self.player.team),
        ]
        self.fallingAnimation = self.jumpingAnimation
        self.shieldAnimation = Animation(0.15, *sprites.shieldImages)
        self.phaseShiftAnimation = Animation(0.15, *sprites.phaseShiftImages)

        self.image = pygame.Surface(self.canvasSize)
        self.image.set_colorkey(self.colourKey)
        self.rect = self.image.get_rect()

    @property
    def pos(self):
        return self.player.pos

    def getAngleFacing(self):
        return self.player.angleFacing

    @property
    def angleFacing(self):
        return self.player.angleFacing

    def __getattr__(self, attr):
        '''
        Proxy attributes through to the underlying player class.
        '''
        return getattr(self.player, attr)

    def update(self):
        self.setImage(self._isMoving(), self._isSlow())

    def _isMoving(self):
        return not (self.player._state['left'] or self.player._state['right'])

    def _isSlow(self):
        # Consider horizontal movement of player.
        if self.player._state['left'] and not self.player._state['right']:
            if self.player._faceRight:
                return True
            else:
                return False
        elif self.player._state['right'] and not self.player._state['left']:
            if self.player._faceRight:
                return False
            else:
                return True
        return False


    def setImage(self, moving, slow):
        flip = None
        sprites = self.app.theme.sprites
        if self.player.ghost:
            blitImages = sprites.ghostAnimation
        elif self.player.turret:
            blitImages = self.turretAnimation
        elif self.player._onGround:
            if isinstance(self.player._onGround, VerticalWall):
                blitImages = self.holdingAnimation
                if self.player._onGround.deltaPt[1] < 0:
                    flip = False
                else:
                    flip = True
                
            elif not moving == 0:
                blitImages = self.standingAnimation
            elif slow:
                blitImages = self.reversingAnimation
            else:
                blitImages = self.runningAnimation
        else:
            if self.player.yVel > 0:
                blitImages = self.fallingAnimation
            else:
                blitImages = self.jumpingAnimation
        self.image.fill(self.image.get_colorkey())
        # Put the pieces together:
        for element in blitImages:
            self.image.blit(element.getImage(), (0,0))
        if self.player.shielded:
            self.image.blit(self.shieldAnimation.getImage(), (0,0))
        if self.player.phaseshift and not defines.useAlpha:
            self.image.blit(self.phaseShiftAnimation.getImage(), (0,0))
        if not self.player._faceRight and flip == None or flip:
            self.image = pygame.transform.flip(self.image, True, False)
        # Flicker the sprite between different levels of transparency
        if defines.useAlpha:
            if self.player.local and self.player.phaseshift:
                self.image.set_alpha(random.randint(30, 150))
            elif self.player.ghost:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
                    
