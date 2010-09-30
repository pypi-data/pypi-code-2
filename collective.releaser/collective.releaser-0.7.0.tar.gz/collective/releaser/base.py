# -*- coding: utf-8 -*-
# Copyright (C)2007 Ingeniweb

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; see the file COPYING. If not, write to the
# Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
from distutils.spawn import find_executable
from tarfile import TarFile
from tarfile import ExtractError
from fnmatch import fnmatch
import logging

import os
import sys

from subprocess import PIPE, Popen
from cStringIO import StringIO

join = os.path.join

# make zc.buildout quiet
#buildout = logging.getLogger('zc.buildout')
#buildout.setLevel(logging.CRITICAL)
#buildout.propagate = False

# create the logger
logger = logging.getLogger('collective.releaser')
logger.setLevel(logging.INFO)
logger.propagate = False
if logger.handlers == []:
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    logger.addHandler(ch)

try:
    # python 2.5
    from subprocess import CalledProcessError
    from subprocess import check_call
except ImportError:
    # python 2.4
    CalledProcessError = Exception
    from subprocess import call

    def check_call(*args, **kw):
        return call(*args, **kw)

def has_svn_support():
    return find_executable('svn') is not None

def savewd(function):
    def _savewd(*args, **kw):
        old = os.getcwd()
        try:
            return function(*args, **kw)
        finally:
            os.chdir(old)
    return _savewd


class ReleaseError(Exception):
    pass

def runwait(command, env={}, debug=False, input=None):
    if env:
        p = Popen(command, env=env, shell=True, stdin=PIPE,
                  stdout=PIPE, stderr=PIPE)
    else:
        p = Popen(command, shell=True, stdin=PIPE,
                  stdout=PIPE, stderr=PIPE)

    if input:
        p.stdin.write(input)
    p.stdin.close()

    stdout = StringIO()
    output = 'x'
    while output:
        output = p.stdout.readline()
        if debug:
            sys.stdout.write(output)
            sys.stdout.flush()
        else:
            stdout.write(output)
    stdout.seek(0)
    return p.wait(), stdout.read(), p.stderr.read()

def system(command, input=''):
    code, o, e = runwait(command, input=input)
    return o + e

def command(cmd):
    """returns a command result"""
    return Popen(cmd, shell=True, stdout=PIPE).stdout

def check_command(cmd):
    """sends a command and check the result"""
    try:
        return check_call(cmd, shell=True) == 0
    except CalledProcessError:
        return False

def get_svn_url():
    """returns current folder's url"""
    svn_info = command('svn info')
    for element in svn_info:
        if element.startswith('URL'):
            return element.split(':', 1)[-1].strip()
    raise ReleaseError('could not find svn info')

def svn_remove(url):
    """checking if the branch exists, if so, override it"""
    if check_command('svn ls %s' % url):
        # removing it
        if not check_command('svn rm %s -m "[releaser] removing branch"' \
                               % url):
            raise ReleaseError("could not remove the existing branch")
        else:
            display('svn path was existing, removed')

def svn_copy(source, target, comment):
    """copy a branch"""
    comment = '[releaser] %s' % comment
    if not check_command('svn cp %s %s -m "%s"' \
                          % (source, target, comment)):
        raise ReleaseError('could not copy %s to %s' % (source, target))
    else:
        display('copied %s to %s' % (source, target))

def svn_mkdir(url):
    """make a dir if not existing"""
    if not check_command('svn ls %s' % url):
        # creating the folder
        if not check_command('svn mkdir %s -m "[releaser] creating folder"' % url):
            raise ReleaseError('could not create the directory %s' % url)

def svn_commit(comment):
    """commits the current directory"""
    comment = '[releaser] %s' % comment
    if not check_command('svn ci -m "%s"' % comment):
        raise ReleaseError('could not commit the trunk')

def svn_rm(url, comment):
    """removes the url, if exists"""
    comment = '[releaser] %s' % comment
    if check_command('svn ls %s' % url):
        if not check_command('svn rm %s -m "%s"' % (url, comment)):
            raise ReleaseError('could not remove %s' % url)
        else:
            display('%s removed' % url)

def svn_cat(url):
    """checkouts"""
    return system('svn cat %s' % url)

def svn_checkout(url, folder):
    """checkouts"""
    if not check_command('svn co %s %s' % (url, folder)):
        raise ReleaseError('could not get %s' % url)

def svn_add(*files):
    """adding files"""
    for file_ in files:
        if not check_command('svn add %s' % file_):
            raise ReleaseError('could not add %s' % file_)

def svn_up(*files):
    """update files"""
    for file_ in files:
        if not check_command('svn up %s' % file_):
            raise ReleaseError('could update %s' % file_)

def safe_input(message, default=None):
    if default is None:
        sdefault = ''
    else:
        sdefault = default
    value = raw_input('%s [%s]: ' % (message, sdefault))
    value = value.strip()
    if value == '':
        return default
    return value

def yes_no_input(message, default='n'):
    show_default = default == 'n' and 'y/N' or 'Y/n'
    value = raw_input('%s [%s]: ' % (message, show_default))
    value = value.strip().lower()
    if not value:
        return default == 'y' and True or False
    if value in ('y', 'yes'):
        return True
    return False

def display(msg):
    print msg
    #    logger.info(msg)  # need to refactor all tests before

def display_step(msg, verbose=False):
    if verbose:
        print msg
    else:
        sys.stdout.write('.')
        sys.stdout.flush()

def package_match(package, exprs):
    include = [expr for expr in exprs if not expr.startswith('!')]
    exclude = [expr[1:] for expr in exprs if expr.startswith('!')]
    founded = []
    for expr in include:
        founded = fnmatch(package, expr) or []
        if founded != []:
            break
    if founded:
        for expr in exclude:
            if fnmatch(package, expr):
                return []
    return founded

