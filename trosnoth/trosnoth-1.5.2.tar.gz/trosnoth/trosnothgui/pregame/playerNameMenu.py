# Trosnoth (UberTweak Platform Game)
# Copyright (C) 2006-2011 Joshua D Bartlett
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

from trosnoth.utils.event import Event
from trosnoth.gui.framework import framework
from trosnoth.gui.framework.elements import (TextButton, TextElement,
        SizedPicture)
from trosnoth.gui.framework.prompt import InputBox
from trosnoth.gui.common import (Area, Location, ScaledScreenAttachedPoint,
        ScaledSize, ScaledPoint)

MAX_NAME_LENGTH = 20

class PlayerNameMenu(framework.CompoundElement):
    def __init__(self, app):
        super(PlayerNameMenu, self).__init__(app)
        self.onGotName = Event()
        myFont = app.screenManager.fonts.bigMenuFont
        self.nameInput = InputBox(app,
                Area(ScaledScreenAttachedPoint(ScaledSize(0, 20), 'center'),
                ScaledSize(300, 60), 'midtop'), font=myFont)
        self.nameInput.onClick.addListener(self.setFocus)
        self.nameInput.onEnter.addListener(lambda sender:self.onOK())
        okButton = TextButton(app,
                Location(ScaledScreenAttachedPoint(ScaledSize(0,110),
                'center'), 'midtop'), 'OK', myFont,
                app.theme.colours.playerNameColour,
                app.theme.colours.playerNameOKMouseover)
        okButton.onClick.addListener(lambda sender:self.onOK())

        bg = pygame.Surface((924, 500))
        bg.fill((64,0,192))
        if app.displaySettings.useAlpha:
            bg.set_alpha(164)

        bp = SizedPicture(app, bg, Location(ScaledPoint(50,160)),
                ScaledSize(924, 570))


        self.elements = [
            bp,
            TextElement(app, 'Please choose a name for your player', myFont,
                Location(ScaledScreenAttachedPoint(ScaledSize(0,-20),
                'center'), 'midbottom'), app.theme.colours.playerNameColour),
            self.nameInput,
            okButton,
        ]
        self.setFocus(self.nameInput)

    def onOK(self):
        # Max name length: 20
        name = self.nameInput.value[:MAX_NAME_LENGTH]
        if name != "":
            self.onGotName.execute(name)
            self.app.identitySettings.setNick(name)
