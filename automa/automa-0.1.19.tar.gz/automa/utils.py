#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Copyright (C) 2010-2011 Marco Pantaleoni. All rights reserved.
# Marco Pantaleoni <marco.pantaleoni@gmail.com>
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 2 as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2010-2011 Marco Pantaleoni"
__license__   = "GPL v2"

from automa.opts import options
from automa.log import *

def dry(action, func, extra_text=""):
    if options.dry_run:
        prefix = "(DRY) " + extra_text
        if not prefix.endswith(' '):
            prefix += ' '
        notify(prefix + action)
        return ""
    prefix = extra_text
    if not prefix.endswith(' '):
        prefix += ' '
    notify(prefix + action)
    return func()

def isWindows():
    import os
    import sys
    if sys.platform == 'win32':
        return True
    if os.name in ('nt', 'ce'):
        return True
    try:
        import platform
        if platform.system() == 'Windows':
            return True
    except ImportError:
        pass
    if os.environ.get('OS','') == 'Windows_NT':
        return True
    try:
        import win32api
        return True
    except ImportError:
        pass
    try:
        import _winreg
        GetVersionEx = sys.getwindowsversion
        return True
    except:
        pass
    return False
