# coding: utf-8

import Xlib.display
import Xlib.X
import Xlib.XK
import Xlib.protocol.event

# http://shallowsky.com/software/crikey/pykey-0.1

special_X_keysyms = {
    ' ' : "space",
    '\t' : "Tab",
    '\n' : "Return",  # for some reason this needs to be cr, not lf
    '\r' : "Return",
    '\e' : "Escape",
    '!' : "exclam",
    '#' : "numbersign",
    '%' : "percent",
    '$' : "dollar",
    '&' : "ampersand",
    '"' : "quotedbl",
    '\'' : "apostrophe",
    '(' : "parenleft",
    ')' : "parenright",
    '*' : "asterisk",
    '=' : "equal",
    '+' : "plus",
    ',' : "comma",
    '-' : "minus",
    '.' : "period",
    '/' : "slash",
    ':' : "colon",
    ';' : "semicolon",
    '<' : "less",
    '>' : "greater",
    '?' : "question",
    '@' : "at",
    '[' : "bracketleft",
    ']' : "bracketright",
    '\\' : "backslash",
    '^' : "asciicircum",
    '_' : "underscore",
    '`' : "grave",
    '{' : "braceleft",
    '|' : "bar",
    '}' : "braceright",
    '~' : "asciitilde"
    }


def get_keysym(ch) :
    keysym = Xlib.XK.string_to_keysym(ch)
    if keysym == 0 :
        # Unfortunately, although this works to get the correct keysym
        # i.e. keysym for '#' is returned as "numbersign"
        # the subsequent display.keysym_to_keycode("numbersign") is 0.
        keysym = Xlib.XK.string_to_keysym(special_X_keysyms[ch])
    return keysym

def is_shifted(ch) :
    if ch.isupper() :
        return True
    if "~!@#$%^&*()_+{}|:\"<>?".find(ch) >= 0 :
        return True
    return False

def char_to_keycode(ch, display) :
    keysym = get_keysym(ch)
    keycode = display.keysym_to_keycode(keysym)
    if keycode == 0 :
        print "Sorry, can't map", ch

    if (is_shifted(ch)) :
        shift_mask = Xlib.X.ShiftMask
    else :
        shift_mask = 0

    return keycode, shift_mask

class Keyboard(object):
    def __init__(self):
        self.display = Xlib.display.Display()
        
    def press_key(self, key):
        keycode, shift_mask = char_to_keycode(key, self.display)
        
        if shift_mask != 0 :
            Xlib.ext.xtest.fake_input(self.display, Xlib.X.KeyPress, 50)
        Xlib.ext.xtest.fake_input(self.display, Xlib.X.KeyPress, keycode)
    
    def release_key(self, key):
        keycode, shift_mask = char_to_keycode(key, self.display)
        
        Xlib.ext.xtest.fake_input(self.display, Xlib.X.KeyRelease, keycode)
        if shift_mask != 0 :
            Xlib.ext.xtest.fake_input(self.display, Xlib.X.KeyRelease, 50)
