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
from automa.path import Path

import re

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

def humanize_seconds(seconds):
    r = int(seconds)

    hh = int(r / 3600)
    r  = r % 3600

    mm = int(r / 60)
    r  = r

    ss = r + (seconds - (hh * 3600 + mm * 60 + r))

    params = dict(hh = hh, mm = mm, ss = ss)
    return "%(hh)02d h %(mm)02d m %(ss)02.2f s" % params

def humanize_bitrate(bitrate):
    v = float(bitrate)

    m_bps = v / 1000000.0
    if m_bps > 1.0:
        return "%.3f mBps" % m_bps

    k_bps = v / 1000.0
    if k_bps > 1.0:
        return "%.3f kBps" % k_bps

    return "%.3f Bps" % v

def humanize_bitrate_byte(bitrate):
    v = float(bitrate)

    v_byte = v / 8.0

    m_bps = v_byte / 1000000.0
    if m_bps > 1.0:
        return "%.3f Mb/s" % m_bps

    k_bps = v_byte / 1000.0
    if k_bps > 1.0:
        return "%.3f Kb/s" % k_bps

    return "%.3f bps" % v

def humanize_filesize(value):
    v = long(value)

    if v > 1000000000L:
        v_gb = float(v) / 1000000000.0
        return "%.3f Gb" % v_gb
    if v > 1000000L:
        v_mb = float(v) / 1000000.0
        return "%.3f Mb" % v_mb
    if v > 1000L:
        v_kb = float(v) / 1000.0
        return "%.3f Kb" % v_kb
    return "%s bytes" % v

def md5_file(pathname):
    """
    Compute the MD5 hash of the file with the given pathname.
    """
    try:
        import hashlib
        m = hashlib.md5()
    except ImportError:
        import md5
        m = md5.new()
    #debug("computing MD5 hash for '%s'..." % pathname)
    fh = open(pathname, 'rb')
    while True:
        block = fh.read(16384)
        if not block:
            break
        m.update(block)
    fh.close()
    return m.hexdigest()

def sha1_file(pathname):
    """
    Compute the SHA-1 hash of the file with the given pathname.
    """
    try:
        import hashlib
        m = hashlib.sha1()
    except ImportError:
        import sha
        m = sha.new()
    #debug("computing SHA-1 hash for '%s'..." % pathname)
    fh = open(pathname, 'rb')
    while True:
        block = fh.read(16384)
        if not block:
            break
        m.update(block)
    fh.close()
    return m.hexdigest()

_var_re = re.compile(r'(\%(?:\([^\(\)]+\))?(?:\#|0|\-| |\+)?[diouxXeEfFgGcrs\%])')

_tobequoted_re = re.compile(r'\s|\'|\"')

def _is_mapping(v):
    if isinstance(v, dict):
        return True
    if hasattr(v, 'keys'):
        return True
    return False

def _is_iterable(v):
    if isinstance(v, (tuple, list)):
        return True
    if hasattr(v, 'keys'):
        return False
    if hasattr(v, '__iter__'):
        return True
    return False

def _escape_string(v):
    if v is None:
        return ''
    if isinstance(v, Path):
        v = str(v)
    if not isinstance(v, basestring):
        v = str(v)
    if _tobequoted_re.search(v):
        return repr(v)
    return v

_escape_var_cycle_map = {}
_escape_var_cycle_level = 0

def _escape_var_expansion(text, v, configsection=None):
    """Return a tuple (text, v) suitable for variable expansion 'text % v'
    where values in v have been properly escaped."""
    from automa.configfile import ConfigSection
    global _escape_var_cycle_map
    new_v = v
    cycle_detected = _escape_var_cycle_map.has_key(id(v))
    _escape_var_cycle_map[id(v)] = True
    if _is_iterable(v):
        if cycle_detected:
            return (text, [])
        assert configsection is None
        new_v = [_escape_string(value) for value in v]
    elif _is_mapping(v):
        if cycle_detected:
            return (text, {})
        if configsection is not None:
            assert isinstance(configsection, ConfigSection) and configsection.value_section
            all_items = v.items() + configsection.items()
        else:
            all_items = v.items()
        new_v = dict([(key, _escape_string(value)) for (key, value) in all_items])
    return (text, new_v)

def _escape_backslash(text):
    """Escape backslash sequences for re.sub() (which expands them otherwise)."""
    n = ''
    l = len(text)
    i = 0
    while i < l:
        ch = text[i]
        if (ch == '\\') and (i+1 < l):
            n += '\\\\' + text[i+1]
            i += 2
            continue
        n += ch
        i += 1
    return n

_dollar_var = re.compile(r'.*?\$\{([a-zA-Z0-9_\.:/\?\~\!\@\#\$\%\^\&\+\|\-]+)\}.*', re.MULTILINE | re.DOTALL)

def _perform_var_subst(text, vars=None, opts=None, configsection=None):
    """Perform '${variable}' interpolation."""
    from automa.configfile import ConfigEntry, ConfigValue, ConfigSection
    from automa.opts import Options

    if not isinstance(text, basestring):
        return text

    def textrepr(value):
        if value is None:
            return ''
        if isinstance(value, Path):
            value = str(value)
        if not isinstance(value, basestring):
            value = str(value)
        if _tobequoted_re.search(value):
            return repr(value)
        return value

    import re
    opts = opts or options
    if not isinstance(opts, (tuple, list)):
        opts = [opts,]
    while True:
        m = _dollar_var.match(text)
        if not m:
            break
        varname  = m.group(1)
        value = None
        found = False
        if configsection is not None:
            assert isinstance(configsection, ConfigSection)
            assert configsection.section_type == ConfigEntry.SECTION_TYPE_SECTION
            if configsection._has_value(varname):
                value = configsection._get_value(varname)
                found = True
        if (not found) and (opts is not None):
            assert isinstance(opts, (tuple, list))
            for opt in opts:
                assert isinstance(opt, Options)
                if opt.has_key(str(varname)):
                    value = opt._getFQ(str(varname))
                    found = True
        if (not found) and (vars is not None):
            if isinstance(vars, Options):
                value = vars._getFQ(varname)
                found = True
            elif isinstance(vars, dict):
                if vars.has_key(varname):
                    value = vars.get(varname, None)
                    found = True
        if not found:
            value = None
        varvalue = textrepr(value)
        text = re.sub(re.escape('${' + varname + '}'), _escape_backslash(varvalue), text)
    return text

def _perform_full_var_expansion_helper(text, vars=None, opts=None, configsection=None):
    """Perform ${variable} interpolation and '%' interpolation."""
    if not isinstance(text, basestring):
        return text
    opts = opts or options
    expanded = _perform_var_subst(text, vars=vars, opts=opts, configsection=configsection)
    if vars is not None:
        (t, v) = _escape_var_expansion(expanded, vars, configsection=configsection)
        expanded = t % v
    return expanded

def _perform_full_var_expansion(text, vars=None, opts=None, configsection=None):
    global _escape_var_cycle_map, _escape_var_cycle_level
    if _escape_var_cycle_level == 0:
        _escape_var_cycle_map = {}
    _escape_var_cycle_level += 1
    result = _perform_full_var_expansion_helper(text, vars=vars, opts=opts, configsection=configsection)
    _escape_var_cycle_level -= 1
    if _escape_var_cycle_level == 0:
        _escape_var_cycle_map = {}
    return result
