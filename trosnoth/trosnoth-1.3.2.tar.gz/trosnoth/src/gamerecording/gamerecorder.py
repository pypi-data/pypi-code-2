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

from trosnoth.src.gamerecording import replays, stats, statgeneration
from trosnoth.src.utils.jsonImport import json
from trosnoth.src.utils.components import Component, Plug, handler
from trosnoth.src.messages import QueryWorldParametersMsg, SetTeamNameMsg
from trosnoth.src.network.networkDefines import validServerVersions
from trosnoth.data import getPath, user, makeDirs
import os
import time
import random

# TODO: put this in a common location, perhaps; removing cyclic dependencies

gameDir = 'recordedGames'
gameExt = '.tros'
replayDir = os.path.join(gameDir, 'replays')
replayExt = '.trosrepl'
statDir = os.path.join(gameDir, 'stats')
statExt = '.trosstat'
htmlDir = os.path.join(gameDir, 'htmlStats')

def checkJson():
    if json is None:
        raise RecordedGameException, 'Cannot write replay without json installed'


def getFilename(alias, directory, ext):
    # Figure out the filename to use for the main file
    gamePath = getPath(user, directory)
    makeDirs(gamePath)
    copyCount = 0
    succeeded = False
    while not succeeded:
        filename = '%s (%s)%s' % (alias, str(copyCount), ext)
        filePath = os.path.join(gamePath, filename)
        succeeded = not os.path.exists(filePath)
        copyCount += 1
    return filePath

# Separate from the server version, which is to do with the
# types and content of network messages.
recordedGameVersion = 2


class RecordedGameException(Exception):
    pass

class GameRecorder(Component):
    inPlug = Plug()
    outPlug = Plug()

    proxyPlug = Plug()    
    
    def __init__(self, alias, version, world):
        super(GameRecorder, self).__init__()
        self.alias = alias
        self.filename = getFilename(self.alias, gameDir, gameExt)
        self.replayFilename = getFilename(self.alias, replayDir, replayExt)
        self.statsFilename = getFilename(self.alias, statDir, statExt)
        self.gameFile = RecordedGameFile(self.filename, serverVersion=version,
                                         alias=alias, replayFilename=self.replayFilename,
                                         statsFilename=self.statsFilename, halfMapWidth=world.map.layout.halfMapWidth,
                                         mapHeight=world.map.layout.mapHeight)
        self.gameFile.save()
        self.statRecorder = stats.StatKeeper(world, self.statsFilename)
        self.replayRecorder = replays.ReplayRecorder(self.replayFilename)
        self.statRecorder.inPlug.connectPlug(self.proxyPlug)
        self.replayRecorder.inPlug.connectPlug(self.proxyPlug)
        
    @inPlug.defaultHandler
    def handleMessage(self, msg):
        self.proxyPlug.send(msg)

    @handler(SetTeamNameMsg, inPlug)
    def teamNameChanged(self, msg):
        self.gameFile.teamNameChanged(msg.teamId, msg.name)
        self.proxyPlug.send(msg)

    def begin(self):        
        self.outPlug.send(QueryWorldParametersMsg(random.randrange(1<<32)))

    def stop(self):
        self.replayRecorder.stop()
        self.statRecorder.stop()
        self.gameFile.gameFinished()


class RecordedGame(object):
    def __init__(self, filename):
        self.filename = filename
        self.gameFile = RecordedGameFile(self.filename)
        self.gameFile.load()
        if not self.gameFile.valid():
            raise RecordedGameException, 'Invalid Game File'

    def serverInformation(self):
        return self.gameFile.serverInformation

    def wasFinished(self):
        return self.gameFile.wasFinished()

    ##
    # Generate an html stats file, and return the url
    def generateHtmlFile(self):
        if self.gameFile.hasHtml():
            return self.gameFile.htmlFile
        # TODO: should try to get the same number in brackets
        self.htmlFile = getFilename(self.gameFile.alias, htmlDir, '.html')
        statgeneration.generateHtml(self.htmlFile, self.gameFile.statsFilename)
        self.gameFile.htmlGenerated(self.htmlFile)
        return self.htmlFile
        
    def __getattr__(self, attr):
        return getattr(self.gameFile, attr)

class RecordedGameFile(object):
    def __init__(self, filename, serverVersion=None, alias=None, replayFilename=None, statsFilename=None, halfMapWidth=None, mapHeight=None):
        self.filename = filename
        self.serverInformation = {}
        self.serverInformation['recordedGameVersion'] = recordedGameVersion
        self.serverInformation['serverVersion'] = serverVersion
        self.serverInformation['alias'] = alias
        self.serverInformation['replayFilename'] = replayFilename
        self.serverInformation['statsFilename'] = statsFilename
        self.serverInformation['dateTime'] = ','.join( map(str,time.localtime()) )
        self.serverInformation['unixTimestamp'] = time.time()
        self.serverInformation['halfMapWidth'] = halfMapWidth
        self.serverInformation['mapHeight'] = mapHeight
        self.serverInformation['teamAname'] = 'Blue'
        self.serverInformation['teamBname'] = 'Red'

    def gameFinished(self):
        self.serverInformation['gameFinishedTimestamp'] = time.time()
        self.save()

    def teamNameChanged(self, teamId, teamName):
        self.serverInformation['team%sname' % (teamId,)] = teamName
        self.save()

    def htmlGenerated(self, filename):
        self.serverInformation['htmlFile'] = filename
        self.save()

    ##
    # Overwrites any existing file
    def save(self):
        # No value may be null
        for value in self.serverInformation.itervalues():
            assert value is not None
        checkJson()
        file = open(self.filename, 'w')
        serverInfoString = json.dumps(self.serverInformation, indent = 4)
        file.write(serverInfoString)
        file.flush()
        file.close()

    def load(self):
        checkJson()
        file = open(self.filename, 'r')
        lines = file.readlines()

        fullText = '\n'.join(lines)
        self.serverInformation = json.loads(fullText)

    def valid(self):
        return self.serverVersion in validServerVersions

    def wasFinished(self):
        return self.serverInformation.has_key('gameFinishedTimestamp')

    def hasHtml(self):
        return self.serverInformation.has_key('htmlFile')

    def __getattr__(self, key):
        return self.serverInformation[key]
