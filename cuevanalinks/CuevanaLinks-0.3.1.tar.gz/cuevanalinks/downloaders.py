#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author: Martín Gaitán <gaitan AT gmail DOT com>
# Licence: GPL v3.0

import os
import sys
import time
import urllib2
import cookielib

from pyquery import PyQuery as pq
from progressbar import ProgressBar, Percentage, Bar, ETA, FileTransferSpeed


def megaupload(url, filename, callback=None, ETA2callback="auto", kbps=96):
    """
    Given a megaupload URL gets the file

    Reproduce this :program:`wget` command::

       $ wget --save-cookies="mu" --load-cookies="mu" \
            -w 45 PUBLIC_MEGAUPLOAD_URL FILE_DIRECT_URL

    :param function callback: the function to callback. It's useful to call 
                              a process over the file before finish download.

    :param ETA_callback: is the :abbr:`ETA (Estimated time to Arrival)` to 
                         make the callback. Should be an :type:`int` (seconds). 
                         The special value ``'auto'`` indicates that
                         the parameter will be estimated as ``file_size / kbps``

    :param int kbps: Kilobytes per seconds. It's a compression level factor.
                     Greater value means wait more until make the callback.
                     ``95`` is a standard compression in cuevana.tv
    """

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )    
    p = pq(url=url, opener=lambda url: opener.open(url).read())
    url_file = p('a.down_butt1').attr('href')
    msg = 'Downloading %s...' #if not callback else 'Buffering %s...'
    countdown(45,  msg % filename)
    try:
        response = opener.open(url_file)
        size = int(response.info().values()[0])

        #import pdb; pdb.set_trace()
    except urllib2.HTTPError, e: 
        print "Problem downloading... :("
        print "Reason: " + e.msg
    else:
        
        chunk = 10240
        if ETA2callback == "auto":
            ETA2callback = size / (kbps * 1024)
            

        my_eta = ETA_callback(ETA2callback, callback)

        widgets = ['', Percentage(), ' ', Bar('='),
                   ' ', my_eta, ' ', FileTransferSpeed()]
        pbar = ProgressBar(widgets=widgets, maxval=size).start()
        with open(filename, 'wb') as localfile:
            copy_callback(response.fp, localfile, size, chunk, 
                            lambda pos: pbar.update(pos),
                            lambda : pbar.finish())
                            
        
def countdown(seconds, msg="Done"):
    """Wait `seconds` counting down.  When is done show the `msg` message
    """
    for i in range(seconds, 0, -1):
        sys.stdout.write("%02d" % i)
        time.sleep(1)
        sys.stdout.write("\b\b")
        sys.stdout.flush()
    sys.stdout.write(msg + "\n")
    sys.stdout.flush()



def copy_callback(src, dest, src_size=None, chunk=10240, 
                    callback_update=None, callback_end=None):
    """
    Copy a file calling back a function on each chunk
    """
    if not src_size:
        src_size = os.stat(src.name).st_size

    cursor = 0 
    while True:
        buffer = src.read(chunk)
        if buffer:
            # ..if not, write the block and continue
            dest.write(buffer)
            if callback_update:
                callback_update(cursor)
            cursor += chunk            
        else:
            break

    if callback_end:
        callback_end()
    
    src.close()
    dest.close()

    # Check output file is same size as input one!
    dest_size = os.stat(dest.name).st_size
    if dest_size != src_size:
        raise IOError(
            "New file-size does not match original (src: %s, dest: %s)" % (
            src_size, dest_size)
        )


class ETA_callback(ETA):
    """ProgressBarWidget for the Estimated Time of Arrival that 
    call back a function when `seconds` left to arrival
    """
    def __init__(self, seconds=-1, callback=None):
        ETA.__init__(self)
        self._seconds = seconds
        self._callback = callback
        self._triggered = False
    
    def update(self, pbar):
        if pbar.currval == 0:
            return 'ETA:  --:--:--'
        elif pbar.finished:
            return 'Time: %s' % self.format_time(pbar.seconds_elapsed)
        else:
            elapsed = pbar.seconds_elapsed
            eta = elapsed * pbar.maxval / pbar.currval - elapsed
            if not self._triggered and eta <= self._seconds and self._callback:
                self._callback()
                self._triggered = True
            return 'ETA:  %s' % self.format_time(eta)
