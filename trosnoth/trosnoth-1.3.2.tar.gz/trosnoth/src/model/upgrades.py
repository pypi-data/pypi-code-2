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

'''upgrades.py - defines the behaviour of upgrades.'''

from math import pi
import random

from trosnoth.src.utils.checkpoint import checkpoint
from trosnoth.src.model.shot import GrenadeShot

from trosnoth.src.messages import FireShotMsg

class Upgrade(object):
    '''Represents an upgrade that can be bought.'''

    # Upgrades have an upgradeType: this must be a unique, single-character
    # value.
    def __init__(self, player):
        self.universe = player.universe
        self.inUse = False
        self.player = player

    def __repr__(self):
        return upgradeNames[type(self)]
    
    def use(self):
        '''Initiate the upgrade (client-side)'''
        pass

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game.'''
        self.inUse = False
        self.player.upgrade = None

    def timeIsUp(self):
        '''
        Called by the universe when the upgrade's time has run out.
        '''

    def goneWhenDie(self):
        return True

class Shield(Upgrade):
    '''Represents a shield; a purchasable upgrade that protects a player from
    one shot'''
    upgradeType = 's'
    requiredStars = 4
    timeRemaining = 30
    shotsCanTake = 1
    def __init__(self, player):
        super(Shield, self).__init__(player)
        self.protections = self.shotsCanTake
        checkpoint('Shield created')

    def use(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.shielded = True
        super(Shield, self).use()
        checkpoint('Shield used (client side)')
            
    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Shield, self).delete()
        self.player.shielded = False
        checkpoint('Shield deleted (client side)')

    def goneWhenDie(self):
        assert False, 'Can\'t die with a shield'        

class PhaseShift(Upgrade):
    '''Represents a phase shift, a purchasable upgrade that means a player cannot
    be shot, but cannot shoot; lasts for a limited time only.'''
    upgradeType = 'h'
    requiredStars = 6
    timeRemaining = 25
    def __init__(self, player):
        super(PhaseShift, self).__init__(player)
        checkpoint('Phase shift created')

    def use(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.phaseshift = True
        super(PhaseShift, self).use()
        checkpoint('Phase shift used (client side)')
            
    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(PhaseShift, self).delete()
        self.player.phaseshift = False
        checkpoint('Phase shift deleted (client side)')

    def goneWhenDie(self):
        assert False, 'Can\'t die with a phase shift'        


class Turret(Upgrade):
    '''Represents a turret; a purchasable upgrade that turns a player into
    a turret; a more powerful player, although one who is unable to move.'''
    upgradeType = 't'
    requiredStars = 8
    timeRemaining = 50
    
    def use(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.turret = True
        self.player._onGround = None
        if self.player.currentZone.turretedPlayer is not None:
            self.player.currentZone.turretPlayer.upgrade.delete()
        self.player.currentZone.turretedPlayer = self.player

        # Arrest vertical movement so that upon losing the upgrade, the
        # player doesn't re-jump
        self.player.yVel = 0

        super(Turret, self).use()
        checkpoint('Turret used (client side)')
        
    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.inUse:
            self.player.turret = False
            self.player.turretOverHeated = False
            self.player.turretHeat = 0.0
            self.player.currentZone.turretedPlayer = None
        super(Turret, self).delete()
        checkpoint('Turret deleted (client side)')      

class MinimapDisruption(Upgrade):
    upgradeType = 'm'
    requiredStars = 15
    timeRemaining = 40

    def use(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.team.opposingTeam.minimapDisrupted = True
        super(MinimapDisruption, self).use()
        checkpoint('Minimap disruption used (client side)')

    def delete(self):
        self.player.team.opposingTeam.minimapDisrupted = False
        super(MinimapDisruption, self).delete()


class Grenade(Upgrade):
    '''represents a grenade that after landing will shoot shots out in all
    directions; after 5 seconds, killing any players hit.'''
    upgradeType = 'g'
    requiredStars = 5
    timeRemaining = 2.5
    numShots = 40
    
    def __init__(self, player):
        self.gr = None                          # Client-side.
        super(Grenade, self).__init__(player)
        checkpoint('Grenade upgrade created')

    def use(self):
        '''Initiate the upgrade.'''
        self.inUse = True

        if self.gr is not None:
            print '** Stray grenade'
            self.gr.delete()

        self.gr = GrenadeShot(self.player.universe, self.player, 'X')

        super(Grenade, self).use()        
        checkpoint('Grenade used (client side)')

    def explode(self):
        # Delete the grenade
        if self.gr is not None:
            self.gr.delete()
            self.gr = None

    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        if self.gr is not None:
            self.explode()
        super(Grenade, self).delete()
        checkpoint('Grenade deleted (client side)')

    def timeIsUp(self):
        print 'Universe declares that grenade should explode'
        playerId = self.player.id
        xpos, ypos = self.gr.pos

        # Fire shots.
        for x in range(0, Grenade.numShots):
            angle = pi*(2*random.random() - 1.0)  # In range (-pi, pi)
            self.universe.eventPlug.send(FireShotMsg(playerId, angle, xpos,
                    ypos, 'G'))

    def goneWhenDie(self):
        return False          

class Ricochet(Upgrade):
    '''Represents a ricochet; a purchasable upgrade that will cause shots to bounce.'''
    upgradeType = 'r'
    requiredStars = 3
    timeRemaining = 10
    def __init__(self, player):
        super(Ricochet, self).__init__(player)
    

    def use(self):
        '''Initiate the upgrade'''
        self.inUse = True
        self.player.hasRicochet = True
        super(Ricochet, self).use()
        checkpoint('Ricochet used (client side)')
            
    def delete(self):
        '''Performs any necessary tasks to remove this upgrade from the game'''
        super(Ricochet, self).delete()
        self.player.hasRicochet = False
        checkpoint('Ricochet delete (client side)')


upgradeOfType = {Shield.upgradeType : Shield,
                 PhaseShift.upgradeType: PhaseShift,
                 Turret.upgradeType : Turret,
                 MinimapDisruption.upgradeType : MinimapDisruption,
                 Grenade.upgradeType : Grenade,
                 Ricochet.upgradeType : Ricochet}

upgradeNames = {Shield : "Shield",
               PhaseShift : "Phase Shift",
               Turret : "Turret",
               MinimapDisruption : "Minimap Disruption",
               Grenade : "Grenade",
               Ricochet : "Ricochet"}
