#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import subprocess
import tempfile

#TODO: Cahge scrot backend to ImageMagic
#      Edit the image
# https://wiki.archlinux.org/index.php/Taking_a_Screenshot
SCREENSHOT_SOUND = '/usr/share/sounds/scru_shot.wav'


class ScrotNotFound(Exception):
    """scrot must be installed"""


def grab(filename, select, sound, quality, delay):
    """Grab the screen as binary file"""
    if not filename:
        # Temporary file
        f = tempfile.NamedTemporaryFile(suffix='.png',
            prefix='screenshot_scrot_')
        filename = f.name
    grab_filename(filename, select, sound, quality, delay)
    # Open the temp screenshot
    return open(filename, 'rb')


def grab_filename(filename, select, sound, quality, delay):
    """Grab the screen as image file"""
    # Wrap of scrot command
    try:
        cmd = ['scrot', filename]
        if select:
            cmd.append('-s')
            cmd.append('-b')    #show window decoration (border)
        if quality:
            cmd.append('-q%d' % quality)
        if delay:
            # delay and show regresive count
            cmd.append('-d%d' % delay)
            cmd.append('-c')
        subprocess.call(cmd)
        if sound:
            play_screenshot_sound()
    except Exception, e:
        raise ScrotNotFound


def play_screenshot_sound():
    """"Play a sound of a camera shot"""
    try:
        # Player for alsa
        subprocess.Popen(['aplay', '-q', SCREENSHOT_SOUND])
    except OSError:
        # Player for oss
        subprocess.Popen(['ossplay', '-q', SCREENSHOT_SOUND])
    else:
        pass
