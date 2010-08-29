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

'''modes.py: defines a set of pre-defined game modes'''


class GameMode(object):
    
    def __init__(self, shotClass, playerClass, grenadeClass):
        self.shotClass = shotClass
        self.playerClass = playerClass
        self.grenadeClass = grenadeClass
        self.Normal()
    
    def _standard(self, pace = 1, fireRate = 1, gravity = 1, jumpHeight = 1,
                   respawnRate = 1, shotSpeed = 1, shotLength = 1, bounce = False, respawnHealth = 1):
        shotClass = self.shotClass
        playerClass = self.playerClass
        grenadeClass = self.grenadeClass

        # Speed that shots travel at.
        shotClass.SPEED = 600 * shotSpeed                      # pix/s
        shotClass.LIFETIME = (1. / shotSpeed) * shotLength     # s
        
        if playerClass is not None:
            # The following values control player movement.
            playerClass.xVel = 360 * pace                  # pix/s
            playerClass.slowXVel = 180 * pace              # pix/s
            playerClass.maxGhostVel = 675. * pace          # pix/s
            playerClass.jumpThrust = 540 * jumpHeight      # pix/s
            playerClass.maxFallVel = 540. * gravity        # pix/s
            playerClass.maxJumpTime = 0.278                # s
            playerClass.gravity = 3672 * gravity           # pix/s/s
            playerClass.ownReloadTime = 1 / 2.7 / fireRate      # s
            playerClass.neutralReloadTime = 1 / 2. / fireRate   # s
            playerClass.enemyReloadTime = 1 / 1.4 / fireRate    # s
            playerClass.turretReloadTime = 0.083 / fireRate     # s
            playerClass.turretHeatCapacity = 2.4 * fireRate
            playerClass.shotHeat = 0.4
            playerClass.respawnTotal = 7.5 / respawnRate
            playerClass.bounce = bounce
            playerClass.respawnHealth = respawnHealth

        if grenadeClass is not None:
            grenadeClass.maxFallVel = 540. * gravity
            grenadeClass.gravity = 1000 * gravity
            grenadeClass.initYVel = -400 * pace
            grenadeClass.initXVel = 200 * pace

    def Lightning(self):
        self._standard(pace = 1.75, fireRate = 2)

    def LowGravity(self):
        self._standard(gravity = 0.25)

    def Normal(self):
        self._standard()

    def FastFire(self):
        self._standard(fireRate = 3, shotSpeed = 2)

    def Insane(self):
        self._standard(pace = 1.75, fireRate = 3, jumpHeight = 2, shotSpeed = 2,
                        shotLength = 2, respawnRate = 60)

    def FastRespawn(self):
        self._standard(respawnRate = 60)

    def Slow(self):
        self._standard(pace = 0.5, gravity = 0.25, jumpHeight = 0.7, shotSpeed = 0.5)

    def HighFastFall(self):
        self._standard(jumpHeight = 2, gravity = 2)

    def Laser(self):
        self._standard(shotSpeed = 30, shotLength = 100)

    def ManyShots(self):
        self._standard(shotLength = 20)

    def ZeroG(self):
        self._standard(gravity = 0.001)

    def AntiG(self):
        self._standard(gravity = -0.1)

    def Bouncy(self):
        self._standard(bounce = True)

    def HighBouncy(self):
        self._standard(bounce = True, jumpHeight = 3)

    def TwoLives(self):
        self._standard(respawnHealth = 2)
