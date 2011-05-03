""" Download utility as easy way to get file from internet
 
    python -m wget <URL>
    python wget.py <URL>

    Placed into Public Domain by anatoly techtonik
    Also available under the terms of MIT license if you need
    Copyright (c) 2010 anatoly techtonik <techtonik@gmail.com>

    Downloads: http://pypi.python.org/pypi/wget/
    Development: http://bitbucket.org/techtonik/python-wget/


    If this module will be included into Python library, it
    is better be renamed to something like 'fetch' to avoid
    complains about missing options.

"""

import sys, urllib, shutil, os, urlparse
import tempfile
import math


__version__ = "0.8"


def filename_from_url(url):
    """:return: detected filename or None"""
    fname = os.path.basename(urlparse.urlparse(url).path)
    if len(fname.strip(" \n\t.")) == 0:
        return None
    return fname

def filename_from_headers(headers):
    """Detect filename from Content-Disposition headers if present.
   http://greenbytes.de/tech/tc2231/

    :param: headers as dict, list or string
    :return: filename from content-disposition header or None
    """
    if type(headers) in (str, unicode):
        headers = headers.splitlines()
    if type(headers) == list:
        headers = dict([x.split(':', 1) for x in headers])
    cdisp = headers.get("Content-Disposition")
    if not cdisp:
        return None
    cdtype = cdisp.split(';')
    if len(cdtype) == 1:
        return None
    if cdtype[0].strip().lower() not in ('inline', 'attachment'):
        return None
    # several filename params is illegal, but just in case
    fnames = [x for x in cdtype[1:] if x.strip().startswith('filename=')]
    if len(fnames) > 1:
        return None
    name = fnames[0].split('=')[1].strip(' \t"')
    name = os.path.basename(name)
    if not name:
        return None
    return name

def get_console_width():
    """Return width of available window area. Autodetection works for
       Windows and POSIX platforms. Returns 80 for others

       Code from http://bitbucket.org/techtonik/python-pager
    """

    if os.name == 'nt':
        STD_INPUT_HANDLE  = -10
        STD_OUTPUT_HANDLE = -11
        STD_ERROR_HANDLE  = -12

        # get console handle
        from ctypes import windll, Structure, byref
        try:
            from ctypes.wintypes import SHORT, WORD, DWORD
        except ImportError:
            # workaround for missing types in Python 2.5
            from ctypes import (
                c_short as SHORT, c_ushort as WORD, c_ulong as DWORD)
        console_handle = windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)

        # CONSOLE_SCREEN_BUFFER_INFO Structure
        class COORD(Structure):
            _fields_ = [("X", SHORT), ("Y", SHORT)]

        class SMALL_RECT(Structure):
            _fields_ = [("Left", SHORT), ("Top", SHORT),
                        ("Right", SHORT), ("Bottom", SHORT)]

        class CONSOLE_SCREEN_BUFFER_INFO(Structure):
            _fields_ = [("dwSize", COORD),
                        ("dwCursorPosition", COORD),
                        ("wAttributes", WORD),
                        ("srWindow", SMALL_RECT),
                        ("dwMaximumWindowSize", DWORD)]

        sbi = CONSOLE_SCREEN_BUFFER_INFO()
        ret = windll.kernel32.GetConsoleScreenBufferInfo(console_handle, byref(sbi))
        if ret == 0:
            return 0
        return sbi.srWindow.Right+1

    elif os.name == 'posix':
        from fcntl import ioctl
        from termios import TIOCGWINSZ
        from array import array

        winsize = array("H", [0] * 4)
        try:
            ioctl(sys.stdout.fileno(), TIOCGWINSZ, winsize)
        except IOError:
            pass
        return (winsize[1], winsize[0])[0]

    return 80

def progress_callback(blocks, block_size, total_size):
    """callback function for urlretrieve that is called when connection is
    created and when once for each block

    draws progress bar (one of free depending on available console wydth:
    [..  ] downloaded / total
    downloaded / total
    [.. ]

    do not display anything if there is not much space on the screen.
    show bytes counter if total_size is unknown as many bytes as possible.

    use sys.stdout.write() instead of "print,", because it allows one more
    symbol at the line end without linefeed on Windows

    :param blocks: number of blocks transferred so far
    :param block_size: in bytes
    :param total_size: in bytes, can be -1 if server doesn't return it
    """
    width = min(100, get_console_width())
    size_width = len("%s" % total_size)
    size_field_width = size_width*2 + 3 # 'xxxx / yyyy'
    min_bar_width = 3 # [.]


    # process special case and return immediately
    if total_size <= 0:
        msg = "\r%s / unknown" % (blocks * block_size)
        if width-1 > 0:
            sys.stdout.write(msg[:width-1]) # leave one character to avoid linefeed
        return


    total_blocks = math.ceil(float(total_size) / block_size)

    # if we need to draw bar
    full_info = (width >= min_bar_width+1+size_field_width+1)
    #                              trailing +1 to avoid linefeed when printing
    size_only = (not full_info and width > size_field_width)
    bar_only = (not size_only and width > min_bar_width)

    # drawing bar
    if full_info:
        bar_width = width-1-size_field_width-1
    elif bar_only:
        bar_width = width-1
   
    if full_info or bar_only:
        # number of dots on thermometer scale
        avail_dots = bar_width-2
        shaded_dots = int(math.ceil(float(blocks) / total_blocks * avail_dots))
        bar = "[%s%s]" % ("."*shaded_dots, " "*(avail_dots-shaded_dots))

    size_info = "%s / %s" % (min(blocks * block_size, total_size), total_size)
    # padding with spaces
    size_info = " "*(size_field_width-len(size_info)) + size_info
    if full_info:
        sys.stdout.write("\r%s %s" % (bar, size_info))
    elif size_only:
        sys.stdout.write("\r%s" % size_info)
    elif bar_only:
        sys.stdout.write("\r%s" % bar)
    else:
        # no space to draw even a lil' bar
        # print blocks, block_size, total_size
        return


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("No download URL specified")

    url = sys.argv[1]

    filename = filename_from_url(url) or "."
    # get filename for temp file in current directory
    (fd, tmpfile) = tempfile.mkstemp(".tmp", prefix=filename+".", dir=".")
    os.close(fd)
    os.unlink(tmpfile)

    (tmpfile, headers) = urllib.urlretrieve(url, tmpfile, progress_callback)
    filenamealt = filename_from_headers(headers)
    if filenamealt:
        filename = filenamealt
    shutil.move(tmpfile, filename)

    print
    print headers
    print "Saved under %s" % os.path.basename(filename)

"""
features that require more tuits for urlretrieve API
http://www.python.org/doc/2.6/library/urllib.html#urllib.urlretrieve

[x] autodetect filename from URL
[x] autodetect filename from headers - Content-Disposition
    http://greenbytes.de/tech/tc2231/
[ ] make HEAD request to detect temp filename from Content-Disposition
[ ] catch KeyboardInterrupt
[ ] optionally preserve incomplete file
[x] create temp file in current directory
[ ] rename temp file automatically if exists
[ ] resume download (broken connection)
[ ] resume download (incomplete file)
[x] show progress indicator
    http://mail.python.org/pipermail/tutor/2005-May/038797.html
[ ] do not overwrite downloaded file
[ ] optionally rename downloaded file automatically if exists
[ ] optionally specify path for downloaded file

[ ] options plan
"""
