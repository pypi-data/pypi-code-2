#!/usr/bin/env python
# coding:utf-8

# lsrSID - Python HVSC browser and sidplay2 GUI.
# Copyright (C) 2010  Daniel Nögel
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import gettext
import hashlib
import distutils
import logging
import tempfile
from distutils import dir_util
from xdg import BaseDirectory

if "vanilla" in sys.argv:
    tempdir = tempfile.mkdtemp()

def md5(file):
    hash = hashlib.md5()
    with open(file, "rb") as fh:
        content = fh.read()
        while content:
            hash.update(content)
            content = fh.read(100)
        
        #~ for i in hash.digest():
            #~ print ord(i)
        return hash.hexdigest()
        

def install_dir():
    try:
        root = __file__
        if os.path.islink(root):
            root = os.path.realpath(root)
        return os.path.dirname(os.path.abspath(root))
    except:
        print("An error occured:")
        print("__file__ not found")
        sys.exit()


def get_user_dir():
    return os.path.expanduser('~')

## Checks file write permissions for the current user
# @return Bool
def is_writeable(path):
    return os.access(path, os.W_OK)


## @todo Return another dir on windows
def get_config_dir():
    if "vanilla" in sys.argv:
        return tempdir
    d = os.path.join(BaseDirectory.xdg_config_home, "lsrsid")
    if not os.path.exists(d):
        dir_util.mkpath(d)
    logging.debug("Config dir: {0}".format(d))
    return d

## @todo Return another dir on windows
def get_data_dir():
    if "vanilla" in sys.argv:
        return tempdir
    d = os.path.join(BaseDirectory.xdg_data_home, "lsrsid")
    if not os.path.exists(d):
        dir_util.mkpath(d)
    logging.debug("Config dir: {0}".format(d))
    return d

def check_dirs(*args):
    for path in args:
        if not os.path.exists(path):
            dir_util.mkpath(path)

def create_dir(path):
    if not os.path.exists(path):
        dir_util.mkpath(os.path.dirname(path))

def translation_gettext():
    path = os.path.join("lsrsidmodules", "locale")
    if not os.path.exists(path):
        path = os.path.join(install_dir(), "locale")
    try:
        trans = gettext.translation('lsrsid', path)
    except IOError:
        trans = gettext.translation('lsrsid', path, ["en_US", "de_DE"])
        print "No language file for you found - using english language file"
    trans.install()

    gettext.bindtextdomain("lsrsid", os.path.join(install_dir(), "locale"))
    gettext.textdomain("lsrsid")
