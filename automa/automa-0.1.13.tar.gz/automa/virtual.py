#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ex:ts=4:sw=4:sts=4:et
# -*- tab-width: 4; c-basic-offset: 4; indent-tabs-mode: t -*-
#
# Blatantly based on Paver virtualenv support module.
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

"""
Tasks for managing virtualenv environments.
"""

__author__    = "Marco Pantaleoni"
__copyright__ = "Copyright (C) 2010 Marco Pantaleoni"
__license__   = "GPL v2"

from automa.opts import options
from automa.tasks import task
from automa.utils import dry
from automa.log import *
from automa.path import Path

from automa.setup_info import version
from automa.shell import _escape_backslash

import os
try:
    import virtualenv
    has_virtualenv = True
except ImportError:
    has_virtualenv = False

_INSTALL_CMD_TEMPLATE = "    subprocess.call([join(%s, 'easy_install'), '%s'])\n"

def _get_install_cmd_func(bin_dir, package, template=_INSTALL_CMD_TEMPLATE):
    return template % (bin_dir, _escape_backslash(package))

if has_virtualenv:
    def _create_bootstrap(script_name, bootstrap_dir,
                          packages_to_install, automa_command_line,
                          install_automa=True, more_text="", dest_dir='.',
                          no_site_packages=False, unzip_setuptools=False,
                          install_cmd_template=_INSTALL_CMD_TEMPLATE,
                          get_install_cmd_func=_get_install_cmd_func,
                          more_text_pre_install="",
                          more_text_post_install=""):
        script_path = script_name
        if bootstrap_dir is not None:
            if not isinstance(bootstrap_dir, Path):
                bootstrap_dir = Path(bootstrap_dir)
            assert isinstance(bootstrap_dir, Path)
            script_path = bootstrap_dir / script_name
            if not bootstrap_dir.exists:
                bootstrap_dir.makedirs()
        if install_automa:
            automa_install = get_install_cmd_func('bin_dir', 'automa==%s' %
                                                  version,
                                                  install_cmd_template)
        else:
            automa_install = ""

        options = ""
        if no_site_packages:
            options = "    options.no_site_packages = True"
        if unzip_setuptools:
            if options:
                options += "\n"
            options += "    options.unzip_setuptools = True"
        if options:
            options += "\n"
        
        extra_text = """def adjust_options(options, args):
    args[:] = ['%s']
%s
def after_install(options, home_dir):
    if sys.platform == 'win32':
        bin_dir = join(home_dir, 'Scripts')
    else:
        bin_dir = join(home_dir, 'bin')
%s""" % (dest_dir, options, automa_install)
        extra_text += more_text_pre_install
        for package in packages_to_install:
            extra_text += get_install_cmd_func('bin_dir', package,
                                               install_cmd_template)
        extra_text += more_text_post_install
        if automa_command_line:
            command_list = []
            command_list.extend(automa_command_line.split(" "))
            extra_text += "    subprocess.call([join(bin_dir, 'automa'),%s)" % repr(command_list)[1:]

        extra_text += more_text
        bootstrap_contents = virtualenv.create_bootstrap_script(extra_text)
        fn = script_path

        debug("Bootstrap script extra text: " + extra_text)
        def write_script():
            p = fn
            if not isinstance(p, Path):
                p = Path(p)
            p.write(bootstrap_contents)
        dry("Write bootstrap script %s" % (fn), write_script)
        
                
    @task
    def bootstrap(ctxt):
        """Creates a virtualenv bootstrap script. 
        The script will create a bootstrap script that populates a
        virtualenv in the current directory. The environment will
        have automa, the packages of your choosing and will run
        the automa command of your choice.
        
        This task looks in the virtualenv options for:
        
        script_name
            name of the generated script
        bootstrap_dir
            directory where the generated script will be put (or None).
            Default to "bootstrap" inside current working directory.
        packages_to_install
            packages to install with easy_install. The version of automa that
            you are using is included automatically. This should be a list of
            strings.
        automa_command_line
            run this automa command line after installation (just the command
            line arguments, not the automa command itself).
        install_automa
            if True, install automa inside the virtual environment (defaults to
            True)
        more_text
            additional text to be added to the bootstrap script after the final
            automa invocation, executed inside the virtual environment
        dest_dir
            the destination directory for the virtual environment (defaults to
            '.')
        no_site_packages
            don't give access to the global site-packages dir to the virtual
            environment (defaults to False)
        unzip_setuptools
            unzip Setuptools when installing it (defaults to False)
        install_cmd_template
            template text for the command used to install packages inside the
            virtual environment. It is processed by the function in
            'get_install_cmd_func'.
            Defaults to:
              "    subprocess.call([join(%s, 'easy_install'), '%s'])\n"
        get_install_cmd_func
            function called to obtain the installation command string to be
            embedded inside the bootstrap script. Defaults to
                lambda bin_dir, package, template=install_cmd_template: \
                    template % (bin_dir, package)
        more_text_pre_install
            additional text to be added to the bootstrap script just before
            the package installation
        more_text_post_install
            additional text to be added to the bootstrap script just after
            the package installation
        """
        vopts = options.virtualenv
        _create_bootstrap(vopts.get("script_name", "bootstrap.py"),
                          vopts.get("bootstrap_dir", os.path.join(os.getcwd(), "bootstrap")),
                          vopts.get("packages_to_install", []),
                          vopts.get("automa_command_line", None),
                          install_automa=vopts.get("install_automa", True),
                          more_text=vopts.get("more_text", ""),
                          dest_dir=vopts.get("dest_dir", '.'),
                          no_site_packages=vopts.get("no_site_packages", False),
                          unzip_setuptools=vopts.get("unzip_setuptools", False),
                          install_cmd_template=vopts.get("install_cmd_template", _INSTALL_CMD_TEMPLATE),
                          get_install_cmd_func=vopts.get("get_install_cmd_func", _get_install_cmd_func),
                          more_text_pre_install=vopts.get("more_text_pre_install", ""),
                          more_text_post_install=vopts.get("more_text_post_install", ""))
