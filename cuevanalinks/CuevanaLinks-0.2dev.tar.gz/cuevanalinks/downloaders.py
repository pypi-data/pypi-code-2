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


def megaupload(url, filename):
    """
    Given a megaupload URL get the file

    Reproduce this :program:`wget` command::

        wget --save-cookies="mu" --load-cookies="mu" \
            -w 45 PUBLIC_MEGAUPLOAD_URL FILE_DIRECT_URL

    """

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener( urllib2.HTTPCookieProcessor(cj) )    
    p = pq(url=url, opener=lambda url: opener.open(url).read())
    url_file = p('a.down_butt1').attr('href')
    countdown(45, 'Downloading %s...' % filename)
    try:
        response = opener.open(url_file)
        size = int(response.info().values()[0])

        #import pdb; pdb.set_trace()
    except urllib2.HTTPError, e: 
        print "Problem downloading... :("
        print "Reason: " + e.msg
    else:
        
        chunk = 10240
        loops = size / chunk + 1    #FIX ME - always + 1 ?
        widgets = ['', Percentage(), ' ', Bar('='),
                   ' ', ETA(), ' ']     #add  FileTransferSpeed()  ?
        pbar = ProgressBar(widgets=widgets, maxval=loops).start()
        
        with open(filename, 'wb') as localfile:
            copy_callback(response.fp, localfile, size, chunk, 
                            lambda pos, total: pbar.update(pos),
                            lambda : pbar.finish())
                            
        
def countdown(seconds, msg="Done"):
    """ 
    Wait `seconds` counting down. 
    When is done show the `msg` message
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
    
    total_loops = src_size / chunk + 1
    cur_block_pos = 0 
    i = 0
    while True:
        cur_block = src.read(chunk)
        if not cur_block:            
            # If it's the end of file
            break
        else:
            # ..if not, write the block and continue
            dest.write(cur_block)
            
            cur_block_pos += chunk            
            i += 1 
            if callback_update:
                callback_update(i, total_loops)
    
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

if __name__ == '__main__':
    megaupload('http://www.megaupload.com/?d=9II6293V', 'hs1x01.mp4')
