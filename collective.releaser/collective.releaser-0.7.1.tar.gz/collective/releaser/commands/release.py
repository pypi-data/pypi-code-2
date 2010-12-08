# -*- coding: utf-8 -*-
""" releaser command
"""
import sys
import os
import re
from os.path import join

from collective.releaser.config import DistutilsMultiConfig
from collective.releaser.commands.extendable import ExtensibleCommand
from collective.releaser.base import (yes_no_input, safe_input, display,
                                      package_match, ReleaseError,
                                      has_svn_support, svn_commit)
from collective.releaser.packet import (get_version, get_name, raise_version,
                                        check_tests, increment_changes,
                                        pypi_upload)
try:
    from msgfmt import Msgfmt
except ImportError:
    from collective.releaser.msgfmt import Msgfmt

class release(ExtensibleCommand):
    """Releaser"""

    description = "Releases an egg"
    user_options = [
            ('release','r', 'release package'),
            ('upload', 'u', 'upload package'),
            ('version=', None, 'new version number'),
            ('auto', 'a', 'automatic mode'),
            ('pre-hook', None, 'Plugins to run before the release'),
            ('post-hook',  None, 'Plugins to run after the release'),
            ('remove-dev-tag', None, 'Automatically remove dev tag'),
        ]

    boolean_options = ['auto', 'remove-dev-tag', 'release', 'upload']
    extensible_options = ['pre-hook', 'post-hook']

    def initialize_options(self):
        """init options"""
        self.testing = False
        self.release = False
        self.upload = False
        self.version = ''
        self.auto = False
        self.post_hook = ['upgrade_change_file', 'mail']
        self.pre_hook = ['raise_version', 'create_svn_tag']
        self.remove_dev_tag = True

    def finalize_options(self):
        """Finalize options."""
        if self.auto and not self.version:
            display('You must specify a version in auto mode')
            sys.argv.append('-h')
            __import__('setup')
            sys.exit(-1)

    def run(self):
        """runner"""
        self.run_extension('pre-hook')
        released = self.make_package_release()
        self.run_extension('post-hook')

    def _validate_command(self, package, server, command='',
                          exprs=None, glob_style=True):
        if command == '':
            command = 'mregister --strict sdist mupload'
        founded = []
        if not glob_style:
            for expr in exprs:
                founded = [r for r in re.findall(expr, package) if
                           r.strip() != '']
                if founded != []:
                    break
        else:
            founded = package_match(package, exprs)
        if founded != []:
            return '%s -r %s' % (command, server)
        return None

    def _get_commands(self, conf, package_name):
        """Reads a conf file and extract the commands to run"""
        commands = []
        glob_style = False
        if 'distutils' not in conf:
            return commands
        distutils = conf['distutils']
        if 'index-servers' in distutils:
            glob_style = distutils.get('glob-style', 'false')
            glob_style = glob_style.strip().lower() == 'true'

            for server_name in distutils.get('index-servers').split('\n'):
                server = server_name.strip()
                if server == '':
                    continue
                server = conf[server]
                command = server.get('release-command', '')
                exprs = [pkg.strip() for pkg in
                         server.get('release-packages', '').split('\n')]
                command = self._validate_command(package_name, server_name,
                                                 command, exprs,
                                                 glob_style)
                if command is not None:
                    if self.remove_dev_tag:
                        command = 'egg_info -RD %s' % command
                    commands.append(command.strip())
        return commands

    def make_package_release(self):
        """Release process."""
        package_name = get_name()
        conf = DistutilsMultiConfig()
        commands = self._get_commands(conf, package_name)
        if commands != []:
            pypi_upload(commands)

        display('%s released' % get_version())
        return len(commands) != 0

