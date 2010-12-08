#############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Bootstrap a buildout-based project

Simply run this script in a directory containing a buildout.cfg.
The script accepts buildout command-line options, so you can
use the -c option to specify an alternate configuration file.

$Id: bootstrap.py 84305 2009-04-16 12:08:01Z tarek $
"""
import glob
import os
import shutil
import sys
import tempfile
import urllib2

EZ_SETUP = 'http://peak.telecommunity.com/dist/ez_setup.py'

eggs_folder = os.path.join(os.path.abspath(os.curdir), 'eggs')
if not os.path.exists(eggs_folder):
    os.mkdir(eggs_folder)
sys.path.insert(0, eggs_folder)

downloads_folder = os.path.join(os.path.abspath(os.curdir), 'downloads')
if not os.path.exists(downloads_folder):
    os.mkdir(downloads_folder)
sys.path.insert(0, downloads_folder)

def _log(msg):
    print msg

def _import(egg_name):
    mod = __import__(egg_name)
    egg_dir = os.path.dirname(mod.__file__)
    egg_dir = os.path.split(egg_dir)[0]
    egg_location = os.path.split(egg_dir)[0]
    if not egg_location.startswith(eggs_folder):
        _log('Copying %s into the buildout' % egg_name)
        path_ = _extract_path(egg_name, egg_location)
        if len(path_) > 0:
            path_ = path_[0]
            folder_name = os.path.split(path_)[-1]
            target = os.path.join(eggs_folder, folder_name)
            if target.lower() == path_.lower():
                return
            if os.path.exists(target):
                shutil.rmtree(target)
            shutil.copytree(path_, target)

def _extract_path(egg_name, folder=eggs_folder):
    egg = glob.glob(os.path.join(folder, '%s-*' % egg_name))
    egg.sort()
    egg.reverse()
    return egg

def link_egg(working_set, egg_name, required=True):
    egg = _extract_path(egg_name)
    if egg != []:
        egg_location = egg[0]
        _log('Using %s from %s' % (egg_name, egg_location))
        working_set.add_entry(egg_name)
        working_set.require(egg_name)
    else:
        try:
            _import(egg_name)
        except ImportError:
            # calling easy_install
            setuptools_parse = pkg_resources.Requirement.parse('setuptools')
            locations = '%s;%s' % (setuptools_parse, eggs_folder)
            PATHS = dict(os.environ, PYTHONPATH=locations)
            cmd = 'from setuptools.command.easy_install import main; main()'
            if sys.platform == 'win32':
                cmd = '"%s"' % cmd # work around spawn lamosity on windows
            else:
                cmd = "'%s'" % cmd
            res = os.system("%s -c %s -mqNxd %s %s" % (sys.executable, cmd, eggs_folder, egg_name))
            _log(res)
            # retrying import
            working_set.add_entry(egg_name)
            working_set.require(egg_name)
            _import(egg_name)

#
# setuptool install
#

# let's try to see if the setuptools is not in the eggs folder already
setuptools = glob.glob(os.path.join(eggs_folder, 'setuptools-*'))
setuptools.sort()
setuptools.reverse()
if setuptools:
    _log('Using setuptools from %s' % setuptools[0])
    sys.path.insert(0, setuptools[0])
    import pkg_resources
else:
    # next, try to see if the environment has it
    try:
        import pkg_resources
        _log('Getting setuptools from %s' % \
             os.path.dirname(pkg_resources.__file__))
    except ImportError:
        _log('Installing setuptools in eggs directory')
        # last option, let's try to get it
        ez = {}
        exec urllib2.urlopen(EZ_SETUP).read() in ez
        ez['use_setuptools'](to_dir=eggs_folder, download_delay=0)

from zc.buildout.buildout import main

ws = pkg_resources.working_set
link_egg(ws, 'zc.buildout')
ws.add_entry(eggs_folder)
main(sys.argv[1:] + ['bootstrap'])

