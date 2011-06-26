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
    author = "Linaro Validation Team",
    author_email = "linaro-dev@lists.linaro.org",
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
    check = lava_dev_tool.commands.check:check
    hack = lava_dev_tool.commands.develop:hack
    track = lava_dev_tool.commands.develop:track
    info = lava_dev_tool.commands.info:info
    install = lava_dev_tool.commands.install:install
    localenv = lava_dev_tool.commands.localenv:localenv
    shell = lava_dev_tool.commands.shell:shell
    status = lava_dev_tool.commands.status:status
    test = lava_dev_tool.commands.test:test
    update = lava_dev_tool.commands.update:update
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'bzr >= 2.4b4',
        'json-schema-validator >= 2.1',
        'lava-tool >= 0.1'],
    setup_requires=[
        'versiontools >= 1.4'],
    tests_require=[
        'mockfs >= 0.2'],
    zip_safe=True)
