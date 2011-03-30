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

import os, sys
import logging
import re

try:
    import paramiko
    has_paramiko = True
except ImportError:
    has_paramiko = False

from automa.opts import options
from automa.tasks import TaskContext
from automa.shell import CommandFailure, _warn_re, _escape_var_expansion
from automa.path import Path
from automa.utils import dry
from automa.log import *

#logging.basicConfig(level = logging.DEBUG)

def _dry(cmdline, host, username, func):
    active_ctxt = TaskContext.Active()
    ssh_tag = "[SSH %s]" % host
    if username:
        ssh_tag = "[SSH %s@%s]" % (username, host)
    if options.dry_run:
        if active_ctxt:
            active_ctxt.notify("(DRY) %s %r" % (ssh_tag, cmdline))
        return ""
    if active_ctxt:
        active_ctxt.notify("%s %r" % (ssh_tag, cmdline))
    return func()

if has_paramiko:
    def _ssh_exec_command(ssh_client, command, bufsize=-1, combine=False):
        assert isinstance(ssh_client, paramiko.SSHClient)
        chan = ssh_client._transport.open_session() 
        chan.set_combine_stderr(combine)
        chan.exec_command(command) 
        stdin = chan.makefile('wb', bufsize) 
        stdout = chan.makefile('rb', bufsize) 
        stderr = chan.makefile_stderr('rb', bufsize) 
        return stdin, stdout, stderr
    
    def ssh(host, cmdline, vars=None, capture=True, ign_errors=None, cwd=None,
            bufsize=1,
            combine_stderr=True,
            port=None, username=None, password=None,
            allow_agent=True, look_for_keys=True,
            auto_add_missing_host=True, **kwargs):
    
        def run_cmd():
            def _perform_var_subst(text):
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
                import main
                while True:
                    m = re.match(r'.*?\$\{([a-zA-Z0-9_.]+)\}.*', text)
                    if not m:
                        break
                    varname  = m.group(1)
                    varvalue = textrepr(options._getFQ(varname))
                    text = re.sub(r'\$\{' + re.escape(varname) + r'\}', varvalue, text)
                return text
    
            ignore_errors = ign_errors
            if ignore_errors is None:
                ignore_errors = options.ignore_errors
        
            cmdline_exe = _perform_var_subst(cmdline)
            if vars is not None:
                (t, v) = _escape_var_expansion(cmdline_exe, vars)
                cmdline_exe = t % v
            ssh_tag = "[SSH %s]" % host
            if username:
                ssh_tag = "[SSH %s@%s]" % (username, host)
            debug("%s ACTUAL COMMAND %r" % (ssh_tag, cmdline_exe))
        
            ssh = paramiko.SSHClient()
            if auto_add_missing_host:
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
            ssh.connect(host, username=username, password=password,
                        allow_agent=allow_agent, look_for_keys=look_for_keys, **kwargs)
    
            stdin, stdout, stderr = None, None, None
            try:
                stdin, stdout, stderr = _ssh_exec_command(ssh, cmdline_exe, bufsize=bufsize,
                                                          combine=combine_stderr)
            except paramiko.SSHException, exc:
                error(repr(exc), ignore_errors=ignore_errors)
                if not ignore_errors:
                    raise CommandFailure("Remote ssh execution exception: %s" % repr(exc))
    
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
            ssh.close()
            if capture:
                if combine_stderr:
                    return p_stdout
                return (p_stdout, p_stderr)
        return _dry(cmdline, host, username, run_cmd)
else:
    def ssh(*args, **kwargs):
        error("paramiko is not installed, and required to use ssh")
        return None
