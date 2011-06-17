#!/usr/bin/env python2
# -*- coding: utf-8 -*-
import subprocess


class XclipNotFound(Exception):
    """xclip must be installed"""


def copy(text):
    """Copy given text into system clipboard."""
    try:
        cmd = ['xclip', '-selection', 'clipboard']
        subprocess.Popen(cmd, stdin=subprocess.PIPE).communicate(
            unicode(text))
    except Exception, e:
        raise XclipNotFound


def paste():
    """Returns system clipboard contents."""
    try:
        cmd = ['xclip', '-selection', 'clipboard', '-o']
        return unicode(
            subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0])
    except Exception, e:
        raise XclipNotFound




