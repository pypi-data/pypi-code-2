#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import clipboard
import imgur
import screenshot
import utils

import os
import subprocess
import urllib

APP_ICON = '/usr/share/icons/hicolor/scalable/apps/scru.svg'
XDG_CACHE_HOME = os.environ['XDG_CACHE_HOME']
APP_CACHE = os.path.join(XDG_CACHE_HOME, 'scru')
if not os.path.isdir(APP_CACHE):
    os.makedirs(APP_CACHE)


def complete(url, notify):
    """Show a notify message when the upload was commpleted"""
    image = urllib.urlretrieve(
    url, os.path.join(APP_CACHE, 'notify.png'))[0]
    image_uri = 'file://' + image
    if notify:
        # Get the thumb image of the current uploaded image
        utils.show_notification('Scru',
            'The screenshot was uploaded to imgur', image_uri)
    print 'The screenshot was uploaded to imgur'
    print 'Link was copied to the clipboard'


def screen_to_imgur(filename, link, select, sound,
                    notify, quality, delay):
    """Take a screenshot and upload to imgur"""
    # Default link argument
    if not link:
        link = 'original'
    # Take the screenshot
    screen = screenshot.grab(filename, select, sound, quality, delay)
    print 'Uploading image to imgur...'
    data = imgur.upload(screen)
    screen.close()
    # Get the links of the uploaded screenshot
    if link == 'html_clikeable_thumbail':
        thumb = data['upload']['links']['large_thumbnail']
        original = data['upload']['links']['original']
        url = '<a href="%s"><img src=%s/></a>' % (original, thumb)
    else:
        url = data['upload']['links'][link]
    notify_im = data['upload']['links']['small_square']    #thumb image
    # Copy to the clipboard the url of the uploaded screenshot
    clipboard.copy(url)
    if notify:
        # Notify when done
        complete(notify_im, notify)
    print link.upper() + ': ' + url
    return url


