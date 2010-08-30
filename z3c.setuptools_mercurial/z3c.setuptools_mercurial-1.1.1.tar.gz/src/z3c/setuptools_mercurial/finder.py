##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
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
"""Find all files checked into a mercurial repository.
"""
import logging
import os
import os.path
import pkg_resources
import subprocess

def get_buildout_version():
    pkg = pkg_resources.working_set.find(
        pkg_resources.Requirement.parse('zc.buildout'))
    if pkg is None:
        return ('00000000',)
    return pkg_resources.parse_version(pkg.version)

def find_files(dirname="."):
    """Find all files checked into a mercurial repository."""
    dirname = os.path.abspath(dirname)
    # Support for zc.buildout 1.5 and higher.
    env = os.environ.copy()
    if 'BUILDOUT_ORIGINAL_PYTHONPATH' in os.environ:
        env['PYTHONPATH'] = os.environ['BUILDOUT_ORIGINAL_PYTHONPATH']
    elif 'PYTHONPATH' in env:
        if get_buildout_version() >= pkg_resources.parse_version('1.5.0'):
            del env['PYTHONPATH']
    try:
        # List all files of the repository as absolute paths.
        proc = subprocess.Popen(['hg', 'locate', '-f'],
                                stderr=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                cwd=dirname,
                                env=env)
        stdout, stderr = proc.communicate()
    except Exception, err:
        logging.error(str(err))
        # If anything happens, return an empty list.
        return []

    # The process finished, but returned an error code.
    if proc.returncode != 0:
        logging.error(stderr+ ' (code %i)' %proc.returncode)
        return []
    # The process finished successfully, so let's use the result. Only select
    # those files that really belong to the passed in directory.
    return [path.replace(dirname+os.path.sep, '')
            for path in stdout.splitlines()
            if path.startswith(dirname)]
