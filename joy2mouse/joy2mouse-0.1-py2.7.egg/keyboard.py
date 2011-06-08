# coding: utf-8

# ----------------------------------------------------------------------------
# joy2mouse - control your mouse with your joystick/joypad
# Copyright (c) 2011 Daniel Nögel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
# ----------------------------------------------------------------------------

import virtkey
import gtk

## This function was found here: http://ubuntuforums.org/showthread.php?t=609804
def keystroke_to_x11(keystroke):
    """ convert "CTRL+Shift+T" to (1<<2 | 1<<0, 28)
        :param keystroke: The keystroke string.
                         - can handle at least one 'real' key
                         - only ctrl, shift and alt supported yet (case-insensitive)
        :returns: tuple: (modifiers, keysym)
    """
    modifiers = 0
    key = ""
    splitted = keystroke.split("+")
    for stroke in splitted:
        lstroke = stroke.lower()
        if lstroke == "ctrl" or lstroke == "control":
            modifiers |= (1 << 2)
        elif lstroke == "shift":
            modifiers |= (1 << 0)
        elif lstroke == "alt":
            modifiers |= (1 << 3) # TODO: right?
        elif len(stroke) == 1:
            key = ord(stroke)
        else: # is a ordinary key (Only one)
            key = gtk.gdk.keyval_from_name(stroke)
    return (modifiers, key)
            
            
class Keyboard(object):
    def __init__(self):
        self.keyboard = virtkey.virtkey()
        
    def press_key(self, keys):
        modifiers, key = keystroke_to_x11(keys)
        
        if modifiers:
            self.keyboard.lock_mod(modifiers)
        try:
            self.keyboard.press_keysym(key)
        finally:
            pass

    def release_key(self, keys):
        modifiers, key = keystroke_to_x11(keys)
        
        try:
            self.keyboard.release_keysym(key)
        finally:
            self.keyboard.unlock_mod(modifiers)
        
        
    
