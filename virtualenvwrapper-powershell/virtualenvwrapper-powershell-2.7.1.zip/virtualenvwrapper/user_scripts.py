#!/usr/bin/env python
# encoding: utf-8
#
# Copyright (c) 2010 Doug Hellmann.  All rights reserved.
#
"""Plugin to handle hooks in user-defined scripts.
"""

import logging
import os
import stat
import subprocess

import pkg_resources

log = logging.getLogger(__name__)


# SHELL_SUFFIX = '.ps1' if os.name == 'nt' else ''
BIN_DIR = 'Scripts' if os.name == 'nt' else 'bin'

def plat_norm(hook_name):
    """Returns appropriate script name for platform.
    """
    if os.name == 'nt':
        return hook_name + '.ps1'
    return hook_name


def run_script(script_path, *args):
    """Execute a script in a subshell.
    """
    if os.path.exists(script_path):
#         with open(script_path, 'rt') as f:
#             print '+' * 80
#             print f.read()
#             print '+' * 80
        cmd = [script_path] + list(args)
        log.debug('running %s', str(cmd))
        try:
            if os.name == 'nt':
                return_code = subprocess.call(["powershell.exe", "-noprofile", "-noninteractive", "-file"] + cmd)
            else:
                return_code = subprocess.call(cmd)
        except OSError, msg:
            log.error('could not run "%s": %s', script_path, str(msg))
        #log.debug('Returned %s', return_code)
    return


def run_global(script_name, *args):
    """Run a script from $WORKON_HOME.
    """
    script_path = os.path.expandvars(os.path.join('$WORKON_HOME', script_name))
    run_script(script_path, *args)
    return


PERMISSIONS = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH


GLOBAL_HOOKS = [
    # initialize
    (plat_norm("initialize"),
     "This hook is run during the startup phase when loading virtualenvwrapper.sh."),

    # mkvirtualenv
    (plat_norm("premkvirtualenv"),
     "This hook is run after a new virtualenv is created and before it is activated."),
    (plat_norm("postmkvirtualenv"),
     "This hook is run after a new virtualenv is activated."),

    # rmvirtualenv
    (plat_norm("prermvirtualenv"),
     "This hook is run before a virtualenv is deleted."),
    ("postrmvirtualenv",
     "This hook is run after a virtualenv is deleted."),

    # deactivate
    (plat_norm("predeactivate"),
     "This hook is run before every virtualenv is deactivated."),
    (plat_norm("postdeactivate"),
     "This hook is run after every virtualenv is deactivated."),

    # activate
    (plat_norm("preactivate"),
     "This hook is run before every virtualenv is activated."),
    (plat_norm("postactivate"),
     "This hook is run after every virtualenv is activated."),

    # get_env_details
    (plat_norm("get_env_details"),
     "This hook is run when the list of virtualenvs is printed so each name can include details."),
    ]

LOCAL_HOOKS = [
    # deactivate
    (plat_norm("predeactivate"),
     "This hook is run before this virtualenv is deactivated."),
    (plat_norm("postdeactivate"),
     "This hook is run after this virtualenv is deactivated."),

    # activate
    (plat_norm("preactivate"),
     "This hook is run before this virtualenv is activated."),
    (plat_norm("postactivate"),
     "This hook is run after this virtualenv is activated."),

    # get_env_details
    (plat_norm("get_env_details"),
     "This hook is run when the list of virtualenvs is printed in 'long' mode so each name can include details."),
    ]


def make_hook(filename, comment):
    """Create a hook script.
    
    :param filename: The name of the file to write.
    :param comment: The comment to insert into the file.
    """
    filename = os.path.expanduser(os.path.expandvars(filename))
    if not os.path.exists(filename):
        log.warning('creating %s', filename)
        f = open(filename, 'w')
        try:
            f.write("""#!%(shell)s
# %(comment)s

""" % {'comment':comment, 'shell':os.environ.get('SHELL', '/bin/sh')})
        finally:
            f.close()
        os.chmod(filename, PERMISSIONS)
    return



# HOOKS


def initialize(args):
    for filename, comment in GLOBAL_HOOKS:
        make_hook(os.path.join('$WORKON_HOME', filename), comment)
    return


def initialize_source(args):
    out = """
#
# Run user-provided scripts
#
[ -f "$WORKON_HOME/initialize" ] && source "$WORKON_HOME/initialize"
"""
    if os.name == 'nt':
        out = """
if (test-path "$env:WORKON_HOME/initialize.ps1") { . "$env:WORKON_HOME/initialize.ps1" }
"""
    return out

def pre_mkvirtualenv(args):
    log.debug('pre_mkvirtualenv %s', str(args))
    envname=args[0]
    for filename, comment in LOCAL_HOOKS:
        make_hook(os.path.join('$WORKON_HOME', envname, BIN_DIR, filename), comment)
    
    run_global(plat_norm('premkvirtualenv'), *args)
    return


def post_mkvirtualenv_source(args):
    out = """
#
# Run user-provided scripts
#
[ -f "$WORKON_HOME/postmkvirtualenv" ] && source "$WORKON_HOME/postmkvirtualenv"
"""
    if os.name == 'nt':
        out = """
if (test-path "$env:WORKON_HOME/postmkvirtualenv.ps1") { . "$env:WORKON_HOME/postmkvirtualenv.ps1" }
"""
    return out


def pre_cpvirtualenv(args):
    log.debug('pre_cpvirtualenv %s', str(args))
    envname=args[0]
    for filename, comment in LOCAL_HOOKS:
        make_hook(os.path.join('$WORKON_HOME', envname, BIN_DIR, filename), comment)
    run_global(plat_norm('precpvirtualenv'), *args)
    return


def post_cpvirtualenv_source(args):
    out = """
#
# Run user-provided scripts
#
[ -f "$WORKON_HOME/postcpvirtualenv" ] && source "$WORKON_HOME/postcpvirtualenv"
"""
    if os.name == 'nt':
        out = """
if (test-path "$env:WORKON_HOME/postcpvirtualenv.ps1") { . "$env:WORKON_HOME/postcpvirtualenv.ps1" }
"""
    return out


def pre_rmvirtualenv(args):
    log.debug('pre_rmvirtualenv')
    run_global(plat_norm('prermvirtualenv'), *args)
    return


def post_rmvirtualenv(args):
    log.debug('post_rmvirtualenv')
    run_global(plat_norm('postrmvirtualenv'), *args)
    return


def pre_activate(args):
    log.debug('pre_activate')
    run_global(plat_norm('preactivate'), *args)
    script_path = os.path.expandvars(os.path.join('$WORKON_HOME', args[0], BIN_DIR, plat_norm('preactivate')))
    run_script(script_path, *args)
    return


def post_activate_source(args):
    log.debug('post_activate')
    out = """
#
# Run user-provided scripts
#
[ -f "$WORKON_HOME/postactivate" ] && source "$WORKON_HOME/postactivate"
[ -f "$VIRTUAL_ENV/bin/postactivate" ] && source "$VIRTUAL_ENV/bin/postactivate"
"""
    if os.name == 'nt':
        out = """
if (test-path "$env:WORKON_HOME/postactivate.ps1") { . "$env:WORKON_HOME/postactivate.ps1" }
if (test-path "$env:VIRTUAL_ENV/Scripts/postactivate.ps1") { . "$env:VIRTUAL_ENV/Scripts/postactivate.ps1" }
"""
    return out


def pre_deactivate_source(args):
    log.debug('pre_deactivate')
    out = """
#
# Run user-provided scripts
#
[ -f "$VIRTUAL_ENV/bin/predeactivate" ] && source "$VIRTUAL_ENV/bin/predeactivate"
[ -f "$WORKON_HOME/predeactivate" ] && source "$WORKON_HOME/predeactivate"
"""
    if os.name == 'nt':
        out = """
if (test-path "$env:VIRTUAL_ENV/Scripts/predeactivate.ps1") { . "$env:VIRTUAL_ENV/Scripts/predeactivate.ps1" }
if (test-path "$env:WORKON_HOME/predeactivate.ps1") { . "$env:WORKON_HOME/predeactivate.ps1" }
"""
    return out

# XXX Unimplemeted for Powershell
def post_deactivate_source(args):
    log.debug('post_deactivate')
    out = """
# Run user-provided scripts

VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV="$WORKON_HOME/%(env_name)s"
[ -f "$WORKON_HOME/%(env_name)s/bin/postdeactivate" ] && source "$WORKON_HOME/%(env_name)s/bin/postdeactivate"
[ -f "$WORKON_HOME/postdeactivate" ] && source "$WORKON_HOME/postdeactivate"
unset VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV
""" % { 'env_name':args[0] }

    if os.name == 'nt':
        out = """
$global:VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV = "$env:WORKON_HOME/%(env_name)s"
if (test-path "$env:WORKON_HOME/%(env_name)s/bin/postdeactivate.ps1") { . "$env:WORKON_HOME/%(env_name)s/bin/postdeactivate.ps1" }
if (test-path "$env:WORKON_HOME/postdeactivate.ps1") { . "$env:WORKON_HOME/postdeactivate.ps1" }
remove-item variable:VIRTUALENVWRAPPER_LAST_VIRTUAL_ENV
"""
    
    return out


def get_env_details(args):
    log.debug('get_env_details')
    run_global(plat_norm('get_env_details'), *args)
    script_path = os.path.expandvars(os.path.join('$WORKON_HOME', args[0], BIN_DIR, plat_norm('get_env_details')))
    run_script(script_path, *args)
    return
