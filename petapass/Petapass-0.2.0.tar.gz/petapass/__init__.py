#!/usr/bin/env python

import hashlib
import hmac
import subprocess
import sys
import optparse

__all__ = ['generate_password', 'copy_to_clipboard']

if sys.platform.startswith('linux'):
    clipcmd = u'xclip -selection c'
elif sys.platform.startswith('darwin'):
    clipcmd = u'pbcopy'
else:
    raise RuntimeError("Unsupported platform: %s"%sys.platform)

def generate_password(master, token):
    """generate a password

    :arg string master: the master password
    :arg string token: an identifier for where the password is used
    :arg bool short: should the generated password be 10 characters or as long as possible
    """
    return hmac.new(master, token, hashlib.sha512).digest().encode('base64')[:10]

def copy_to_clipboard(s):
    """copy string s to the clipboard"""
    with subprocess.Popen(clipcmd.split(), stdin=subprocess.PIPE).stdin as pipe:
        pipe.write(s)
