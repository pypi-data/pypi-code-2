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

from trosnoth.src.utils.event import Event
from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.framework.elements import TextButton, TextElement
from trosnoth.src.gui.framework.prompt import InputBox
from trosnoth.src.gui.common import *
from trosnoth.src.trosnothgui.defines import *
from trosnoth.data import getPath, user
from trosnoth.src.utils.getUserInfo import writeName

class PlayerNameMenu(framework.CompoundElement):
    def __init__(self, app):
        super(PlayerNameMenu, self).__init__(app)
        self.onGotName = Event()
        myFont = app.screenManager.fonts.bigMenuFont
        self.nameInput = InputBox(app, Area(ScaledScreenAttachedPoint(ScaledSize(0, 20), 'center'), ScaledSize(300, 60), 'midtop'), font = myFont)
        self.nameInput.onClick.addListener(self.setFocus)
        self.nameInput.onEnter.addListener(lambda sender:self.onOK())
        okButton = TextButton(app, Location(ScaledScreenAttachedPoint(ScaledSize(0,70), 'center'), 'midtop'), 'OK', myFont, (192,0,0), (0,192,0))
        okButton.onClick.addListener(lambda sender:self.onOK())
        self.elements = [
            TextElement(app, "Please choose a name for your player", myFont, Location(ScaledScreenAttachedPoint(ScaledSize(0,-20), 'center'), 'midbottom'), (128,255,128)),
            self.nameInput,
            okButton
            ]
        self.setFocus(self.nameInput)
        

    def onOK(self):
        # Max name length: 20
        name = self.nameInput.value[:maxNameLength]
        if name != "":
            self.onGotName.execute(name)
            writeName(name)