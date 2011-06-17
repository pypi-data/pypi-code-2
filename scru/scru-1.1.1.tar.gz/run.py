#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import plac
import scru
import time

"""
Scru
=====
    Screenshot Uploader

python 2.7 +
OS: linux
"""
#TODO: GUI version (PyQt)

__autor__ = 'Roberto Gea (Alquimista)'

# version number: {major}.{minor}.{maintenance}
# major: big changes (new stuff, or a lot of small changes)
# minor: small changes (small changes)
# maintenance: bugfix or refactoring
__version__ = '1.1.1'

#TODO: embed codes
LINKS = ['small_square', 'large_thumbnail',
         'imgur_page', 'original', 'delete_page',
         'html_clikeable_thumbail']


@plac.annotations(
    version=('output version information and exit', 'flag', 'v'),
    sound=('notification screenshot sound', 'flag', 's'),
    notify=('notify of the uploaded screenshot', 'flag', 'n'),
    noupload=("only screenshot", 'flag', 'noup', None, None, True),
    output=("screenshot filename", 'option', 'o', str, None, 'FILENAME'),
    window=('interactively select a window or rectangle with the mouse.',
            'flag', 'w', True),
    link=('link to get from the image uploaded to imgur.'
          '\nLinks: ' + str(LINKS), 'option', 'l', str, LINKS, 'URL'),
    quality=('image quality (1-100) high value means  high  size,'
             'low  compression.\nDefault: 75. (Effect differs depending on '
             'file format chosen).', 'option', 'q', int, None, 'NUM'),
    delay=('wait NUM seconds before taking a shot, and display a countdown',
           'option', 'd', int, None, 'NUM'))
def main(version, sound, notify, noupload, output,
         window, link, quality, delay):
    if version:
        print 'scru version ' + __version__
    else:
        if noupload:
            if not output:
                # ignore notify and link arguments ()
                # (nothing to notify, no link to show)
                name = 'SCREENSHOT_%G%S'
                output = time.strftime(name, time.localtime()) + '.png'
                screenshot = scru.screenshot.grab(output, window, sound,
                                                  quality, delay)
                screenshot.close()
        else:
            scru.screen_to_imgur(
                output, link, window, sound, notify, quality, delay)


if __name__ == '__main__':
    plac.call(main)

