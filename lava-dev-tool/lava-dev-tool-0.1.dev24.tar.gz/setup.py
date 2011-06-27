#!/usr/bin/env python
#
# Copyright (C) 2010, 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of lava-dev-tool
#
# lava-dev-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# lava-dev-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with lava-dev-tool.  If not, see <http://www.gnu.org/licenses/>.


try:
    from setuptools import setup, find_packages
except ImportError:
    print "This package requires setuptools to be configured"
    print "It can be installed with debian/ubuntu package python-setuptools"
    raise


setup(
    name='lava-dev-tool',
    version=":versiontools:lava_dev_tool:",
    author="Linaro Validation Team",
    author_email="linaro-dev@lists.linaro.org",
    url="http://launchpad.net/lava-dev-tool/",
    packages=find_packages(),
    description=(
        "LAVA development tool is a reproducible builder and release helper"
        " focused on complex python projects"),
    test_suite='lava_dev_tool.tests.test_suite',
    license="LGPLv3",
    entry_points="""
    [console_scripts]
    lava-dev-tool = lava_dev_tool.main:main
    [lava_dev_tool.commands]
    hack = lava_dev_tool.commands.component:hack
    track = lava_dev_tool.commands.component:track
    build = lava_dev_tool.commands.component:build
    clean = lava_dev_tool.commands.component:clean
    install = lava_dev_tool.commands.component:install
    uninstall = lava_dev_tool.commands.component:uninstall
    test = lava_dev_tool.commands.component:test
    update = lava_dev_tool.commands.component:update
    info = lava_dev_tool.commands.project:info
    check = lava_dev_tool.commands.project:check
    status = lava_dev_tool.commands.project:status
    sequence = lava_dev_tool.commands.project:sequence
    init = lava_dev_tool.commands.project:init
    localenv = lava_dev_tool.commands.localenv:localenv
    shell = lava_dev_tool.commands.localenv:shell
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'bzr >= 2.4b4',
        'json-schema-validator >= 2.1',
        'lava-tool >= 0.1',
        'virtualenv >= 1.4.9'],
    setup_requires=[
        'versiontools >= 1.4'],
    tests_require=[
        'mockfs >= 0.2'],
    zip_safe=True)
