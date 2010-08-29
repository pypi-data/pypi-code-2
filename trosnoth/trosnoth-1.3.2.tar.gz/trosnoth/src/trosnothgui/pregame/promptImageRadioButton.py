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

from trosnoth.src.gui.framework.dialogbox import DialogBox, DialogResult, DialogBoxAttachedPoint
from trosnoth.src.trosnothgui.pregame.imageRadioButton import ImageRadioButton
from trosnoth.src.gui.framework.elements import PictureElement, TextElement, TextButton
from trosnoth.src.gui.framework.prompt import InputBox, intValidator
from trosnoth.src.gui.framework import framework
from trosnoth.src.gui.common import *

class CustomPrompt(DialogBox, framework.TabFriendlyCompoundElement):
    def __init__(self, app, width=2, height=1):
        super(CustomPrompt, self).__init__(app, ScaledSize(400,230),
                "Custom Size")
        colours = app.theme.colours

        # Half width input and label
        widthText = TextElement(app, "Half Width:",
                app.screenManager.fonts.bigMenuFont,
                Location(DialogBoxAttachedPoint(self, ScaledSize(260,10)),
                'topright'), colours.radioSelected)
        self.width = InputBox(app, Area(DialogBoxAttachedPoint(self,
                ScaledSize(280,10)), ScaledSize(80,50)),
                str(width), font=app.screenManager.fonts.bigMenuFont,
                validator=intValidator, maxLength=2)
        self.width.onClick.addListener(self.setFocus)
        self.width.onTab.addListener(self.tabNext)
        self.width.onEnter.addListener(lambda sender: self.ok())         

        # Height input and label
        heightText = TextElement(app, "Height:",
                app.screenManager.fonts.bigMenuFont,
                Location(DialogBoxAttachedPoint(self, ScaledSize(260,75)),
                'topright'), colours.radioSelected)
        self.height = InputBox(app, Area(DialogBoxAttachedPoint(self,
                ScaledSize(280,75)), ScaledSize(80,50)),
                str(height), font=app.screenManager.fonts.bigMenuFont,
                validator=intValidator, maxLength=2)
        self.height.onClick.addListener(self.setFocus)
        self.height.onTab.addListener(self.tabNext)
        self.height.onEnter.addListener(lambda sender: self.ok())
        
        font = app.screenManager.fonts.dialogButtonFont

        # OK Button
        okButton = TextButton(app,  Location(DialogBoxAttachedPoint(self,
                ScaledSize(115,160))), "OK", font, colours.dialogButtonColour,
                colours.radioMouseover)
        okButton.onClick.addListener(lambda sender: self.ok())

        # Cancel Button
        cancelButton = TextButton(app,  Location(DialogBoxAttachedPoint(self,
                ScaledSize(195,160))), "Cancel", font,
                colours.dialogButtonColour, colours.radioMouseover)
        cancelButton.onClick.addListener(lambda sender: self.cancel())

        # Add elements to screen
        self.elements = [self.height, self.width, widthText, heightText,
                okButton, cancelButton]
        self.tabOrder = [self.width, self.height]
        self.setFocus(self.width)
        self.setColours(colours.dialogBoxEdgeColour,
                colours.dialogBoxTextColour, colours.dialogBoxTextColour)

    def ok(self):
        self.result = DialogResult.OK
        self.value = (int(self.width.value), int(self.height.value))
        self.Close()
        
    def cancel(self):
        self.result = DialogResult.Cancel
        self.value = None
        self.Close()

class PromptImageRadioButton(ImageRadioButton):
    def __init__(self, app, text, area):
        customFont = app.screenManager.fonts.customSizeButtonFont
        self.imageCustom= TextImage("?", customFont, (0,0,0))
        
        super(PromptImageRadioButton, self).__init__(app, text, area,
                self.imageCustom)
        self.value = None
    def _beforeSelected(self):
        if self.value:
            self.box = CustomPrompt(self.app, self.value[0], self.value[1])
        else:
            self.box = CustomPrompt(self.app)
        self.box.onClose.addListener(self._boxClosed)
        self.box.Show()
        return False

    def deselected(self):
        super(PromptImageRadioButton, self).deselected()
        self.imageCustom.text = "?"

    def _boxClosed(self):
        if self.box.result == DialogResult.OK:
            width, height = self.box.value
            if width > 30:
                width = 30
            if width == 0:
                width = 1
            if height > 30:
                height = 30
            if height == 0:
                height = 1
            self.value = (width, height)
            
            self.imageCustom.text = "%d x %d" % self.value
            self.group.selected(self)
