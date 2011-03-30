#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Blatantly based on Paver sh function.
#
# The original copyright notice is:
# 
#     Copyright (c) 2008, SitePen, Inc. and Kevin Dangoor
#     All rights reserved.
#    
#     Redistribution and use in source and binary forms, with or without
#     modification, are permitted provided that the following conditions are met:
#     
#        * Redistributions of source code must retain the above copyright notice,
#          this list of conditions and the following disclaimer.
#        * Redistributions in binary form must reproduce the above copyright notice,
#          this list of conditions and the following disclaimer in the documentation
#          and/or other materials provided with the distribution.
#        * Neither the name of SitePen, Inc. nor the names of its contributors
#          may be used to endorse or promote products derived from this software
#          without specific prior written permission.
#     
#     THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#     ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#     WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#     DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#     ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#     (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#     LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
#     ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#     (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#     SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#     
#     Portions copyright Ned Batchelder, Ian Bicking and Michael Foord.
#
# Modifications by Marco Pantaleoni are:
#
# Copyright (C) 2010 Marco Pantaleoni. All rights reserved
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
__copyright__ = "Copyright (C) 2010 Marco Pantaleoni"
__license__   = "GPL v2"

import subprocess
import sys, os

from automa.opts import options
from automa.tasks import TaskContext
from automa.path import Path
from automa.utils import dry
from automa.log import *

import re

DEFAULT_SHELL = "/bin/bash"

_warn_re = re.compile(r'(?:(^|\b)(warn|warning|err|error|fail|failure|failed|critical|exception|traceback|broken|couldn\'t|can\'t|cannot|can not)(\b|$))|(?:warning|error|failed|failure|critical|exception|traceback|broken)', re.IGNORECASE)

_var_re = re.compile(r'(\%(?:\([^\(\)]+\))?(?:\#|0|\-| |\+)?[diouxXeEfFgGcrs\%])')

_tobequoted_re = re.compile(r'\s|\'|\"')

class CommandFailure(Exception):
    """Command execution failure."""
    pass

def _dry(cmdline, func):
    return dry("%r" % cmdline, func, extra_text="SHELL")

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

def _escape_var_expansion(text, v):
    """Return a tuple (text, v) suitable for variable expansion 'text % v'
    where values in v have been properly escaped."""
    new_v = v
    if _is_iterable(v):
        new_v = [_escape_string(value) for value in v]
    elif _is_mapping(v):
        new_v = dict([(key, _escape_string(value)) for (key, value) in v.items()])
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

def _perform_var_subst(text):
    """Perform '${variable}' substitution."""
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
    while True:
        m = re.match(r'.*?\$\{([a-zA-Z0-9_.]+)\}.*', text)
        if not m:
            break
        varname  = m.group(1)
        varvalue = textrepr(options._getFQ(varname))
        text = re.sub(re.escape('${' + varname + '}'), _escape_backslash(varvalue), text)
    return text

def cd(path, vars=None):
    olddir = Path(os.getcwd())
    if isinstance(path, Path):
        debug("CD %r" % path)
        path.chdir()
        return olddir
    actual_path = _perform_var_subst(path)
    if vars is not None:
        (t, v) = _escape_var_expansion(actual_path, vars)
        actual_path = t % v
    actual_path = Path(actual_path)
    if actual_path != path:
        debug("CD %r (from %r)" % (actual_path, path))
    else:
        debug("CD %r" % actual_path)
    actual_path.chdir()
    return olddir

def sh(cmdline, vars=None, capture=True, ign_errors=None, cwd=None,
       shell=DEFAULT_SHELL, bufsize=1,
       combine_stderr=True):
    """
    Runs a command through the shell.
    If capture is True, the output of the command will be returned as a string.
    If the command has a non-zero return code and ignore_errors is False, a
    CommandFailure exception is raised. If ignore_errors is True, non-zero
    return codes are silently ignored.
    
    If the dry_run option is True, the command will not be run.
    """
    def run_cmd():
        ignore_errors = ign_errors
        if ignore_errors is None:
            ignore_errors = options.ignore_errors

        cmdline_exe = _perform_var_subst(cmdline)
        if vars is not None:
            (t, v) = _escape_var_expansion(cmdline_exe, vars)
            cmdline_exe = t % v
        debug("ACTUAL COMMAND %r" % cmdline_exe)
        kwargs = {'shell': True, 'cwd': cwd, 'executable': shell,
                  'bufsize': bufsize,
                  'stdin': None, 'stdout': None, 'stderr': None}
        if sys.platform == 'win32':
            kwargs['shell'] = False
            kwargs['executable'] = None
        if capture:
            if combine_stderr:
                kwargs['stderr'] = subprocess.STDOUT
            else:
                kwargs['stderr'] = subprocess.PIPE
            kwargs['stdout'] = subprocess.PIPE
        p = subprocess.Popen(cmdline_exe, **kwargs)

        p_stdout = None
        p_stderr = None
        if capture:
            info("OUTPUT:")
            p_stdout = ""
            line = p.stdout.readline()
            while line:
                if line.endswith("\n"):
                    line = line[:-1]
                logfunc = info
                if _warn_re.search(line):
                    logfunc = warn
                logfunc(line, extra_indent=1)
                p_stdout += line + "\n"
                line = p.stdout.readline()
            if not combine_stderr:
                info("STDERR:")
                p_stderr = ""
                line = p.stderr.readline()
                while line:
                    if line.endswith("\n"):
                        line = line[:-1]
                    logfunc = info
                    if _warn_re.search(line):
                        logfunc = warn
                    logfunc(line, extra_indent=1)
                    p_stderr += line + "\n"
                    line = p.stderr.readline()
        else:
            p_stdout = p.communicate()[0]
        if p.returncode:
            if capture:
                if combine_stderr:
                    error(p_stdout, ignore_errors=ignore_errors)
                else:
                    error(p_stderr, ignore_errors=ignore_errors)
            if not ignore_errors:
                raise CommandFailure("Subprocess return code: %d" % p.returncode)

        if capture:
            if combine_stderr:
                return p_stdout
            return (p_stdout, p_stderr)

    return _dry(cmdline, run_cmd)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
