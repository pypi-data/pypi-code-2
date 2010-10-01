#!/usr/bin/env python
"""Simple sound players.

All sound players are based on Tkinter and some will use
the "pygame" sound package if it is available.

History:
2003-11-17 ROwen
2004-08-11 ROwen    Define __all__ to restrict import.
2005-06-08 ROwen    Changed BellPlay, SoundPlayer, NoPLay to new-style classes.
2009-10-22 ROwen    Modified to use pygame instead of snack to play sound files.
"""
__all__ = ['bell', 'BellPlay', 'SoundPlayer', 'NoPlay']

import sys
import Tkinter
import RO.StringUtil
try:
    import pygame.mixer
    _PyGameAvail = True
except ImportError:
    _PyGameAvail = False
# wait to initialize pygame.mixer until the first SoundPlayer is created
# to avoid creating a Tk root window before it's wanted
# (in case we use Tk to play the bell sound directly)
_PyGameReady = False

_TkWdg = None

def bell(num=1, delay=100):
    """Rings the bell num times using tk's bell command.
    
    Inputs:
    - num   number of times to ring the bell
    - delay delay (ms) between each ring
    
    Note: always rings at least once, even if num < 1
    """
    global _TkWdg
    if not _TkWdg:
        _TkWdg = Tkinter.Frame()
    _TkWdg.bell()
    if num > 1:
        _TkWdg.after(int(delay), bell, int(num)-1, int(delay))

class BellPlay(object):
    """An object that rings the bell num times.
    
    Inputs:
    - num   number of times to ring the bell
    - delay delay (ms) between each ring
    
    Note: always rings at least once, even if num < 1
    """
    def __init__(self,
        num = 1,
        delay = 100,
    ):
        """Similar to bell, but pre-checks data and supports the "play" method
        """
        try:
            assert int(num) >= 0
        except (ValueError, TypeError, AssertionError):
            raise ValueError("num=%r must be a nonnegative integer" % (num,))
        try:
            assert int(delay) >= 0
        except (ValueError, TypeError, AssertionError):
            raise ValueError("delay=%r must be a nonnegative integer" % (delay,))
        
        self._num = num
        self._delay = delay
        
    def play(self):
        """Play the sound"""
        bell(self._num, self._delay)

class SoundPlayer(object):
    """An object that plays a sound file using pygame (if available), else rings the bell.
    
    Inputs:
    - fileName  name of sound file
    - bellNum   number of times to ring the bell (<1 is treated as 1)
    - bellDelay delay (ms) between each ring
    
    The bell data is used if pygame is not available or the file
    is not a valid sound file.
    """
    def __init__(self,
        fileName = None,
        bellNum = 1,
        bellDelay = 100,
    ):
        global _PyGameAvail, _PyGameReady
        if _PyGameAvail and not _PyGameReady:
            try:
                pygame.mixer.init()
                _PyGameReady = True
            except Exception, e:
                sys.stderr.write("Could not initialize pygame for sound: %s\n" % \
                    (RO.StringUtil.strFromException(e),))
                _PyGameAvail = False
            
        self._snd = None
        self._bell = BellPlay(bellNum, bellDelay)
        self._fileName = fileName

        if _PyGameReady and fileName:
            try:
                self._snd = pygame.mixer.Sound(fileName)
            except Exception, e:
                sys.stderr.write("Could not load sound file %r; using beep instead: %s\n" % \
                    (fileName, RO.StringUtil.strFromException(e),))
        
        if not self._snd:
            self._snd = BellPlay(num=bellNum, delay=bellDelay)
    
    def play(self):
        """Play the sound.
        """
        try:
            self._snd.play()
        except (SystemExit, KeyboardInterrupt):
            raise
        except Exception:
            self._bell.play()

    def getFile(self):
        """Returns a tuple: file name, file loaded.
        
        "File loaded" is True if the file was successfully loaded.
        This does not quite guarantee that the file can be played;
        if pygame is mis-installed then it is possible to laod sounds
        but not play them.
        """
        fileLoaded = (self._snd != None)
        return (self._fileName, fileLoaded)
        
class NoPlay(object):
    def play(self):
        pass
