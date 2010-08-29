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

'''
trosnoth.src.network.trosnothdiscoverer
This module provides a facade for the network game discovery protocol. This
facade only shows information about Trosnoth games.
'''

from twisted.internet import defer

from trosnoth.data import getPath, user
from trosnoth.src.utils.unrepr import unrepr
from trosnoth.src.network.discoverer import DiscoveryHandler
from trosnoth.version import fullVersion

DATA_KIND = 'TrosnothGame'
AGENT = 'trosnoth-%s' % (fullVersion,)

class TrosnothDiscoverer(object):
    def __init__(self, netman, upstream=None):
        if upstream is not None:
            self.discoverer = DiscoveryHandler(netman, AGENT, upstream,
                    DATA_KIND)
        else:
            self.discoverer = DiscoveryHandler(netman, AGENT,
                    dataKind=DATA_KIND)

        if netman.getTCPPort() != 6789:
            # If we're a second trosnoth client, try to connect to the first one.
            self.discoverer.tryAddress(('127.0.0.1', 6789))

        try:
            f = open(getPath(user, 'peers'), 'r')
        except IOError:
            pass
        else:
            self.discoverer.loadPeers(f)
            f.close()

    def kill(self):
        # Save peers.
        f = open(getPath(user, 'peers'), 'w')
        self.discoverer.savePeers(f)
        f.close()

        # Stop it.
        self.discoverer.kill()

    def setGame(self, info):
        '''
        Sets the details of the currently running game. Should be called when
        a new server is started and when game details change.
        '''
        key = '\x00'    # Could be used for multiple games on one host.
        value = repr(info)

        self.discoverer.setData(DATA_KIND, key, value)

    def delGame(self):
        '''
        Deletes the local game. Should be called when a game is
        over or no longer accepting connections.
        '''
        key = '\x00'

        self.discoverer.delData(DATA_KIND, key)

    def getGames(self):
        '''
        Returns a deferred returning a collection of known games.
        '''
        def gotGames(data):
            if data is None:
                return None     # Could not connect.
            result = []
            for address, kind, key, value, location in data:
                try:
                    info = unrepr(value)
                except:
                    continue
                if not isinstance(info, dict):
                    continue

                result.append((address, info, location))
            return result

        deferred = self.discoverer.getData(DATA_KIND)
        deferred.addCallback(gotGames)

        return deferred

    def isInternetAccessible(self):
        return self.discoverer.isInternetAccessible()

