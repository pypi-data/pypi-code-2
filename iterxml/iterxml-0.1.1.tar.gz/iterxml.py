# -*- coding: utf-8 -*-
#
#  iterxml.py
#  iterxml
# 
#  Created by Lars Yencken on 13-07-2010.
#  Copyright 2010 Lars Yencken. All rights reserved.
#


"""
A library for iterating through large xml files.
"""

import os
from xml.etree import cElementTree as ElementTree
import bz2
import gzip
import subprocess

USE_SHELL = (os.name == 'posix')

def iterxml(stream_or_file, tag_of_interest, use_shell=USE_SHELL):
    """
    When passed a stream or filename and a tag of interest, returns an
    iterator over matching nodes in the stream. If a filename is given with
    standard gzip or bz2 file extensions, the file is transparently
    decompressed.
    
    The iteration destructively removes node history after each element is
    parsed, in order to allow parsing of files whose contents are too large
    to fit into memory.

    If use_shell is set to True, a unix shell is used to run gzip or bz2 can
    in a separate process. On a POSIX platform this is the default. Otherwise,
    files are opened and decompressed natively in Python.
    """
    if isinstance(stream_or_file, (str, unicode)):
        istream = _open_stream(stream_or_file, use_shell)
    else:
        istream = stream_or_file

    context = iter(ElementTree.iterparse(istream, events=('start', 'end')))
    event, root = context.next()
    root = root

    for event, node in context:
        if event == 'end' and node.tag == tag_of_interest:
            yield node
            root.clear()

def _open_stream(filename, use_shell=USE_SHELL):
    if filename.endswith('.bz2'):
        if use_shell:
            return _bzip_pipe(filename)
        else:
            return bz2.BZ2File(filename, 'r')

    elif filename.endswith('.gz'):
        if use_shell:
            return _gzip_pipe(filename)
        else:
            return gzip.GzipFile(filename, 'r')

    return open(filename, 'r')

def _bzip_pipe(filename):
    p = subprocess.Popen(['bunzip2', '-c', filename], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    p.stdin.close()
    return p.stdout

def _gzip_pipe(filename):
    p = subprocess.Popen(['gunzip', '-c', filename], stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)
    p.stdin.close()
    return p.stdout

# vim: ts=4 sw=4 sts=4 et tw=78:
