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

from trosnoth.data import getPath, user
from trosnoth.src.utils import unrepr
from trosnoth.src.trosnothgui import defines

def loadSettingsFile(filename):
    filename = getPath(user, filename)
    try:
        fileHandle = open(filename, 'r')
        s = fileHandle.read()
        d = unrepr.unrepr(s)
        if not isinstance(d, dict):
            d = {}
    except IOError:
        d = {}
    return d

class DisplaySettings(object):
    '''
    Stores the Trosnoth display settings.
    '''
    DEFAULT_THEME = 'default'

    def __init__(self, app):
        self.app = app

        self.reset()

    def reset(self):
        # Attempt to load the settings from file.
        data = loadSettingsFile('display')

        self.size = data.get('size', defines.screenSize)
        self.fullScreen = data.get('fullscreen', defines.fullScreen)
        self.useAlpha = data.get('usealpha', defines.useAlpha)
        self.smoothPanning = data.get('smoothPanning', True)
        self.centreOnPlayer = data.get('centreOnPlayer', False)
        self.fsSize = data.get('fsSize', self.size)
        self.theme = data.get('theme', self.DEFAULT_THEME)
        self.showObstacles = data.get('showObstacles', False)

        defines.useAlpha = self.useAlpha

    def getSize(self):
        if self.fullScreen:
            return self.fsSize
        else:
            return self.size

    def apply(self):
        '''
        Apply the current settings.
        '''
        defines.useAlpha = self.useAlpha

        size = self.getSize()

        # Don't bother changing the screen if the settings that matter haven't changed
        if (size != self.app.screenManager.size) or (self.fullScreen !=
                self.app.screenManager.isFullScreen()):
            # Tell the main program to change its screen size.
            self.app.changeScreenSize(size, self.fullScreen)

    def save(self):
        '''
        Save the values to file.
        '''
        # Write to file
        displayFilename = getPath(user, 'display')
        displayFile = open(displayFilename, 'w')
        displayFile.write(repr({
            'size': self.size,
            'fullscreen': self.fullScreen,
            'usealpha': self.useAlpha,
            'smoothPanning': self.smoothPanning,
            'centreOnPlayer': self.centreOnPlayer,
            'fsSize': self.fsSize,
            'theme': self.theme,
        }))
        displayFile.close()
        
class SoundSettings(object):
    '''
    Stores the Trosnoth display settings.
    '''

    def __init__(self, app):
        self.app = app

        self.reset()

    def reset(self):
        # Attempt to load the settings from file.
        data = loadSettingsFile('sound')

        self.soundEnabled = data.get('playSound', True)
        self.musicEnabled = data.get('playMusic', True)
        self.musicVolume = data.get('musicVolume', 100)
        self.soundVolume = data.get('soundVolume', 100)

    def apply(self):
        '''
        Apply the current settings.
        '''

        if self.musicEnabled != self.app.musicManager.isMusicPlaying():
            if self.musicEnabled:
                self.app.musicManager.playMusic()
            else:
                self.app.musicManager.stopMusic()

        self.app.musicManager.setVolume(self.musicVolume)

        if self.soundEnabled:
            self.app.soundPlayer.setMasterVolume(self.soundVolume / 100.)
        else:
            self.app.soundPlayer.setMasterVolume(0)

    def save(self):
        '''
        Save the values to file.
        '''
        # Write to file
        filename = getPath(user, 'sound')
        dataFile = open(filename, 'w')
        dataFile.write(repr({
            'playSound': self.soundEnabled,
            'playMusic': self.musicEnabled,
            'musicVolume': self.musicVolume,
            'soundVolume': self.soundVolume
        }))
        dataFile.close()
        

