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
themes.py
This module defines the interface to the various different themes.
'''

import os
import pygame

from trosnoth import data
from trosnoth.src.gui.fonts.font import Font, ScaledFont
from trosnoth.src.gui.framework.basics import SingleImage, Animation
from trosnoth.src.trosnothgui import defines
from trosnoth.src.model.map import MapLayout
from trosnoth.src.utils.unrepr import unrepr

def teamColour(colourId):
    def colourFunction(self, team):
        return self.getTeamColour(team, colourId)
    return colourFunction

class ThemeColours(object):
    def getTeamColour(self, team, colourId):
        teamNum = ord(team.id) - 64
        return getattr(self, 'team%d%s' % (teamNum, colourId))

    sysMessageColour = teamColour('msg')
    backgroundColour = teamColour('bg')
    chatColour = teamColour('chat')
    miniMapZoneOwnColour = teamColour('Mn_zone')
    miniMapOrbOwnColour = teamColour('Mn_mk')
    miniMapPlayerColour = teamColour('Mn_pl')
    miniMapGhostColour = teamColour('Mn_gh')

def cachedProperty(fn):
    def spriteFunction(self):
        try:
            return self._store[fn]
        except KeyError:
            self._store[fn] = result = fn(self)
            return result
    return property(spriteFunction)

def cached(fn):
    def spriteFunction(self, *args):
        try:
            return self._store[fn, args]
        except KeyError:
            self._store[fn, args] = result = fn(self, *args)
            return result
    return spriteFunction

def image(path, colourkey=(255, 255, 255), alpha=False):
    def imageFunction(self):
        return self.theme.loadSprite(path, colourkey, alpha)
    return cachedProperty(imageFunction)

def images(paths, colourkey=(255, 255, 255), alpha=False):
    def imageFunction(self):
        return self.theme.loadSprites(paths, colourkey, alpha)
    return cachedProperty(imageFunction)

def wrappedImage(path):
    def imageFunction(self):
        return SingleImage(self.theme.loadSprite(path))
    return cachedProperty(imageFunction)

class ThemeSprites(object):
    def __init__(self, theme):
        self.theme = theme
        self._store = {}

    pointer = image('pointer.bmp')
    smallStar = image('smallstar.png')
    star = image('star.png')
    grenade = image('grenade.bmp')
    neutralOrb = image('greyOrb.png')

    playerHead = wrappedImage('headOutline.png')
    playerBody = wrappedImage('Body-1.png')
    turretBase = wrappedImage('TurretBase.png')
    playerStanding = wrappedImage('Legs-S0.png')
    playerJumping = wrappedImage('Legs-R3.png')

    runningLegs = images(['Legs-R1.png', 'Legs-R2.png',
            'Legs-R3.png', 'Legs-R4.png'])
    backwardsLegs = images(['Legs-W1-3.png', 'Legs-W1-2.png',
            'Legs-W1-1.png', 'Legs-W1.png'])

    shieldImages = images(['shieldImage1.png', 'shieldImage2.png',
            'shieldImage3.png', 'shieldImage4.png'])
    phaseShiftImages = images(['phaseShift1.png', 'phaseShift2.png',
            'phaseShift3.png', 'phaseShift4.png'])

    @cachedProperty
    def ghostAnimation(self):
        if defines.useAlpha:
            ghostAnimation = self.theme.loadSprites(['ghost.png',
                'ghost2.png', 'ghost3.png', 'ghost4.png', 'ghost3.png',
                'ghost2.png'])
        else:
            ghostAnimation = self.theme.loadSprites(['ghost.bmp', 'ghost2.bmp',
                'ghost3.bmp', 'ghost4.bmp', 'ghost3.bmp', 'ghost2.bmp'])
        return [Animation(0.25, *ghostAnimation)]

    @cached
    def playerHolding(self, team):
        return SingleImage(self.theme.loadTeamSprite('Hold-1', team.id))

    @cached
    def gunImages(self, team):
        return self.theme.loadTeamSprites([
            'Head-4', 'Head-3', 'Head-2',
            'Head-1', 'Head-0', 'Head-17',
            'Head-16','Head-15', 'Head-14'
        ], team.id)
        
    @cached
    def playerTeam(self, team):
        if team.id == 'A':
            path = 'Blue.png'
        elif team.id == 'B':
            path = 'Red.png'
        else:
            path = 'White.png'
        return SingleImage(self.theme.loadSprite(path, (0, 0, 0)))

    @cached
    def orb(self, team):
        if team.id == 'A':
            path = 'blueOrb.png'
        elif team.id == 'B':
            path = 'redOrb.png'
        else:
            return self.neutralOrb
        return self.theme.loadSprite(path)

    @cached
    def shotAnimation(self, team):
        if team.id == 'A':
            colour = 'blue'
        else:
            colour = 'red'
        return self.theme.makeShot(colour)

    @cached
    def interfaceBackground(self, kind, team1, team2):
        '''
        kind is the map block kind ('fwd' or 'bck')
        team1 and team2 are the owners of the two halves of the map. This is
            represented as the team id or '\x00' (neutral) or None (out of
            bounds).
        '''
        if kind == 'fwd':
            return pygame.transform.flip(self.interfaceBackground('bck', team1,
                    team2), False, True)
        elif kind != 'bck':
            raise AssertionError('%r is not a valid interface map block kind' %
                    (kind,))

        c = self.theme.colours
        colours = {'A' : c.team1bg,
                   'B' : c.team2bg,
                   '\x00' : c.neutral_bg,
                   None : (0, 0, 0)}

        img = pygame.surface.Surface((MapLayout.zoneInterfaceWidth, \
                                      MapLayout.halfZoneHeight))
        rect = img.get_rect()
        pts1 = (rect.topleft, rect.bottomright, rect.bottomleft)
        pts2 = (rect.topleft, rect.topright, rect.bottomright)
        pygame.draw.polygon(img, colours[team1], pts1)
        pygame.draw.polygon(img, colours[team2], pts2)
        img.set_colorkey((0, 0, 0))
        
        return img

class Theme(object):
    def __init__(self, app):
        self.app = app
        self.paths = []
        self.colours = ThemeColours()
        self.sprites = ThemeSprites(self)
        self.setTheme(app.displaySettings.theme)

    def setTheme(self, themeName):
        '''
        Sets the theme to the theme with the given name.
        '''
        self.name = themeName
        self.paths = [data.getPath(data.user), data.getPath(data)]

        def insertPath(p):
            if os.path.exists(p):
                self.paths.insert(0, p)
        insertPath(data.getPath(data.themes, themeName))
        insertPath(data.getPath(data.user, 'themes', themeName))
        self.initFonts()
        self.initSounds()
        self.initColours()

    def initColours(self):
        colourPath = self.getPath('config', 'colours.cfg')
        colourData = self._getColourData(colourPath)
        defaultColours = self._getColourData(data.getPath(data))

        for colourName, colour in defaultColours.iteritems():
            if colourName in colourData:
                colour = colourData[colourName]
            setattr(self.colours, colourName, colour)

    def initSounds(self):
        # TODO: actual sounds
        #self.app.soundPlayer.addSound('tag.ogg', 'tag', 1)
        #self.app.soundPlayer.addSound('shoot.ogg', 'shoot', 8)
        pass

    def initFonts(self):
        fontData = self._getFontData()

        for fontName, defaultDetails in DEFAULT_FONTS.iteritems():
            if fontName in fontData:
                fontFile, size = fontData[fontName]
            else:
                fontFile, size = defaultDetails

            if fontName in UNSCALED_FONTS:
                font = Font(fontFile, size)
            else:
                font = ScaledFont(fontFile, size)
            self.app.fonts.addFont(fontName, font)

    def _getFontData(self):
        try:
            fontLines = open(self.getPath('config', 'fonts.cfg')).readlines()
        except IOError:
            return {}

        result = {}
        for line in fontLines:
            bits = line.split("=")
            bits[2] = bits[2].strip()
            # Perform basic checks
            if len(bits) != 3 or not bits[2].isdigit():
                print 'Invalid font config line: %r' % (line,)
            else:
                result[bits[0]] = (bits[1], int(bits[2]))
        return result

    def _getColourData(self, filepath):
        try:
            lines = open(self.getPath('config', 'colours.cfg')).readlines()
        except IOError:
            return {}

        result = {}
        for line in lines:
            line = line.strip()
            if line == '' or line.startswith('#'):
                continue
            bits = line.split("=", 1)
            # Perform basic checks
            invalid = False
            if len(bits) != 2:
                invalid = True
            else:
                try:
                    colour = unrepr(bits[1])
                except:
                    invalid = True
                if (not isinstance(colour, tuple) or len(colour) < 3 or
                        len(colour) > 4):
                    invalid = True
            if invalid:
                print 'Invalid colour config line: %r' % (line,)
            else:
                result[bits[0].strip()] = colour
        return result

    def getPath(self, *pathBits):
        '''
        Returns a path to the given themed file, looking in the following
        locations:
         1. User theme files for the current theme.
         2. Built-in theme files for the current theme.
         3. Default files.
        '''
        for path in self.paths:
            path = os.path.join(path, *pathBits)
            if os.path.isfile(path):
                return path
        raise IOError('file not found: %s' % (os.path.join(*pathBits),))

    def loadSprite(self, filename, colourkey=(255, 255, 255), alpha=False):
        '''
        Loads the sprite with the given name. A colour key of None may be given
        to disable colourkey transparency.
        '''
        filepath = self.getPath('sprites', filename)
        image = pygame.image.load(filepath)

        if alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

        if colourkey is not None:
            image.set_colorkey(colourkey)

        return image

    def loadSprites(self, filenames, colourkey=(255, 255, 255), alpha=False):
        images = []
        for filename in filenames:
            images.append(self.loadSprite(filename, colourkey, alpha))
        return images

    def makeShot(self, colour):
        '''
        Creates the shot sprite / animation. This is here because the Pirate
        theme needs the shot to spin, which it does not normally do.
        '''
        shotImg = self.loadSprite('%sShot.bmp' % (colour,))

        if self.name != 'pirate':
            return SingleImage(shotImg)

        numShotImages = 5
        degree = (360 / numShotImages)

        shots = [pygame.transform.rotate(shotImg, degree * i) for i in range(0,
                numShotImages)]
        return Animation(0.07, *shots)

    def loadTeamSprite(self, filename, teamId):
        '''
        teamId must be 'A' or 'B'.
        If teamId is 'A', grabs <filename>.png
        If teamId is 'B', grabs <filename>b.png if it exists, or <filename>.png
            otherwise.
        '''
        if teamId == 'B':
            fullFilename = '%sb.png' % (filename,)
            try:
                filepath = self.getPath('sprites', fullFilename)
                if not os.path.isfile(filepath):
                    fullFilename = '%s.png' % (filename,)
            except IOError:
                fullFilename = '%s.png' % (filename,)
        elif teamId == 'A':
            fullFilename = '%s.png' % (filename,)
        else:
            raise ValueError('teamId must be A or B, not %r' % (teamId,))

        return self.loadSprite(fullFilename)

    def loadTeamSprites(self, filenames, teamId):
        images = []
        for filename in filenames:
            images.append(self.loadTeamSprite(filename, teamId))
        return images

DEFAULT_FONTS = {
    'default': ('FreeSans.ttf', 24),
    'defaultTextBoxFont': ('FreeSans.ttf', 20),
    'unobtrusivePromptFont': ('FreeSans.ttf', 28),
    'chatFont': ('FreeSans.ttf', 25),

    'winMessageFont': ('FreeSans.ttf', 72),

    'nameFont': ('FreeSans.ttf', 20),

    'hugeMenuFont': ('FreeSans.ttf', 54),
    'bigMenuFont': ('FreeSans.ttf', 36),
    'mainMenuFont': ('FreeSans.ttf', 36),
    'serverListFont': ('FreeSans.ttf', 24),
    'timerFont': ('FreeSans.ttf', 32),
    'consoleFont': ('FreeSans.ttf', 32),
    'ampleMenuFont': ('FreeSans.ttf', 40),
    'mediumMenuFont': ('FreeSans.ttf', 36),
    'menuFont': ('FreeSans.ttf', 30),
    'ingameMenuFont': ('FreeSans.ttf', 12),
    'versionFont': ('FreeSans.ttf', 16),
    'scrollingButtonsFont': ('FreeSans.ttf', 24),
    'zoneBarFont': ('FreeSans.ttf', 24),
    'dialogButtonFont': ('KLEPTOCR.TTF', 50),

    'customSizeButtonFont': ('KLEPTOCR.TTF', 100),
                           
    'messageFont': ('FreeSans.ttf', 20),
    'leaderboardFont': ('KLEPTOCR.TTF', 21),
    
    'smallNoteFont': ('FreeSans.ttf', 22),
    'labelFont': ('FreeSans.ttf', 32),
    'captionFont': ('FreeSans.ttf', 35),
    'keymapFont': ('FreeSans.ttf', 24),
    'keymapInputFont': ('FreeSans.ttf', 20),

    'connectionFailedFont': ('FreeSans.ttf', 32),

    'creditsFont': ('FreeSans.ttf', 24),
    'creditsH2': ('KLEPTOCR.TTF', 48),
    'creditsH1': ('KLEPTOCR.TTF', 60),
}

UNSCALED_FONTS = set([
    'nameFont',
    'ingameMenuFont',
])
