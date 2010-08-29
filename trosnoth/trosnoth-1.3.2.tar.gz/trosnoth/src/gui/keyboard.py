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

import pygame.locals as pgl
import pygame
import UserDict

# 1. We want to be able to represent a shortcut as a string.
def shortcutName(key, modifiers=0):
    # pygame.key.name() could also work.
    try:
        name = NAMED[key]
    except KeyError:
        name = pygame.key.name(key)

    # Add the modifiers.
    modString = ''
    for kmod, modName in KMOD_NAMES:
        if modifiers & kmod:
            modString = '%s%s+' % (modString, modName)

    return '%s%s' % (modString, name)

NAMED = {pgl.K_BACKSPACE: 'Backspace', pgl.K_BREAK: 'Break', pgl.K_CAPSLOCK: 'Capslock',
         pgl.K_CLEAR: 'Clear', pgl.K_DELETE: 'Del', pgl.K_DOWN: 'Down', pgl.K_END: 'End',
         pgl.K_ESCAPE: 'Escape', pgl.K_EURO: 'Euro', pgl.K_F1: 'F1', pgl.K_F2: 'F2', pgl.K_F3: 'F3', pgl.K_F4: 'F4',
         pgl.K_F5: 'F5', pgl.K_F6: 'F6', pgl.K_F7: 'F7', pgl.K_F8: 'F8', pgl.K_F9: 'F9', pgl.K_F10: 'F10',
         pgl.K_F11: 'F11', pgl.K_F12: 'F12', pgl.K_F13: 'F13', pgl.K_F14: 'F14', pgl.K_F15: 'F15',
         pgl.K_FIRST: 'First', pgl.K_HELP: 'Help', pgl.K_HOME: 'Home', pgl.K_INSERT: 'Ins',
         pgl.K_LALT: 'L.Alt', pgl.K_LAST: 'Last', pgl.K_LCTRL: 'L.Ctrl', pgl.K_LEFT: 'Left',
         pgl.K_LMETA: 'L.Meta', pgl.K_LSHIFT: 'L.Shift', pgl.K_LSUPER: 'L.Super',
         pgl.K_MENU: 'Menu', pgl.K_MODE: 'Mode', pgl.K_NUMLOCK: 'Numlock', pgl.K_PAGEDOWN: 'PgDn',
         pgl.K_PAGEUP: 'PgUp', pgl.K_PAUSE: 'Pause', pgl.K_POWER: 'Power', pgl.K_PRINT: 'Print',
         pgl.K_RALT: 'R.Alt', pgl.K_RCTRL: 'R.Ctrl', pgl.K_RETURN: 'Return',
         pgl.K_RIGHT: 'Right', pgl.K_RMETA: 'R.Meta', pgl.K_RSHIFT: 'R.Shift',
         pgl.K_RSUPER: 'R.Super', pgl.K_SCROLLOCK: 'Scrolllock', pgl.K_SYSREQ: 'SysRq',
         pgl.K_TAB: 'Tab', pgl.K_UP: 'Up', pgl.K_SPACE: 'Space',

         pgl.K_a: 'a', pgl.K_b: 'b', pgl.K_c: 'c', pgl.K_d: 'd', pgl.K_e: 'e', pgl.K_f: 'f', pgl.K_g: 'g',
         pgl.K_h: 'h', pgl.K_i: 'i', pgl.K_j: 'j', pgl.K_k: 'k', pgl.K_l: 'l', pgl.K_m: 'm', pgl.K_n: 'n',
         pgl.K_o: 'o', pgl.K_p: 'p', pgl.K_q: 'q', pgl.K_r: 'r', pgl.K_s: 's', pgl.K_t: 't', pgl.K_u: 'u',
         pgl.K_v: 'v', pgl.K_w: 'w', pgl.K_x: 'x', pgl.K_y: 'y', pgl.K_z: 'z', pgl.K_0: '0', pgl.K_1: '1',
         pgl.K_2: '2', pgl.K_3: '3', pgl.K_4: '4', pgl.K_5: '5', pgl.K_6: '6', pgl.K_7: '7', pgl.K_8: '8',
         pgl.K_9: '9', pgl.K_KP0: 'keypad-0', pgl.K_KP1: 'keypad-1', pgl.K_KP2: 'keypad-2',
         pgl.K_KP3: 'keypad-3', pgl.K_KP4: 'keypad-4', pgl.K_KP5: 'keypad-5', pgl.K_KP6: 'keypad-6',
         pgl.K_KP7: 'keypad-7', pgl.K_KP8: 'keypad-8', pgl.K_KP9: 'keypad-9', pgl.K_KP_DIVIDE: 'keypad divide',
         pgl.K_KP_ENTER: 'keypad enter', pgl.K_KP_EQUALS: 'keypad equals', pgl.K_KP_MINUS: 'keypad minus',
         pgl.K_KP_MULTIPLY: 'keypad asterisk', pgl.K_KP_PERIOD: 'keypad full stop', pgl.K_KP_PLUS: 'keypad plus',
         
         pgl.K_AMPERSAND: '&', pgl.K_ASTERISK: '*', pgl.K_AT: '@', pgl.K_BACKQUOTE: '`', pgl.K_BACKSLASH: '\\',
         pgl.K_CARET: '^', pgl.K_COLON: ':', pgl.K_COMMA: ',', pgl.K_DOLLAR: '$', pgl.K_EQUALS: '=',
         pgl.K_EXCLAIM: '!', pgl.K_GREATER: '>', pgl.K_LESS: '<', pgl.K_HASH: '#', pgl.K_LEFTBRACKET: '[',
         pgl.K_LEFTPAREN: '(', pgl.K_MINUS: '-', pgl.K_PERIOD: '.', pgl.K_PLUS: '+', pgl.K_QUOTE: "'",
         pgl.K_RIGHTBRACKET: ']', pgl.K_RIGHTPAREN: ')', pgl.K_SEMICOLON: ';', pgl.K_SLASH: '/',
         pgl.K_UNDERSCORE: '_'
         }

KMOD_NAMES = ((pgl.KMOD_CTRL, 'Ctrl'), (pgl.KMOD_ALT, 'Alt'), \
              (pgl.KMOD_META, 'Meta'), (pgl.KMOD_SHIFT, 'Shift'))


# VirtualKeySet is a mapping from name -> default value.
class VirtualKeySet(UserDict.UserDict):
    pass

# KeyboardMapping is a mapping from key -> virtual key name.
class KeyboardMapping(UserDict.UserDict):
    def __init__(self, virtualKeys):
        self.virtualKeys = virtualKeys
        UserDict.UserDict.__init__(self, ((default, vk) for (vk, default) in virtualKeys.iteritems()))

    def load(self, string):
        '''Restores a keyboard mapping from a configuration string.'''
        # Reset to defaults.
        self.data = {}

        # Update from string.
        unmappedKeys = dict(self.virtualKeys)
        for record in string.split('\n'):
            if record == '':
                continue
            key, vk = record.split(':')
            self.data[int(key)] = vk
            if vk in unmappedKeys:
                del unmappedKeys[vk]

        # Fill in any unmapped keys from the defaults if possible.
        for vk, default in unmappedKeys.iteritems():
            if default not in self.data:
                self.data[default] = vk

    def save(self):
        '''Returns a configuration string for this keyboard mapping.'''
        records = ['%d:%s' % item for item in self.data.iteritems()]
        return '\n'.join(records)
   
    def getkey(self, action):
        '''Returns one key that results in the given action or raises KeyError.'''
        for k, v in self.data.iteritems():
            if v == action:
                return k
        raise KeyError(action)
