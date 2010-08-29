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

from trosnoth.src.gui.framework.elements import TextButton
from trosnoth.src.gui.common import *

def button(app, text, onClick, pos, anchor='topleft', hugeFont=False):
    pos = Location(ScaledScreenAttachedPoint(ScaledSize(pos[0], pos[1]), anchor), anchor)
    if hugeFont:
        font = app.screenManager.fonts.hugeMenuFont
    else:
        font = app.screenManager.fonts.mainMenuFont
    result = TextButton(app, pos, text, font, app.theme.colours.mainMenuColour,
            app.theme.colours.white)
    result.onClick.addListener(lambda sender: onClick())
    return result
