#!/usr/bin/env python
#
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of launch-control-tool.
#
# launch-control-tool is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# launch-control-tool is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with launch-control-tool.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages


setup(
    name='launch-control-tool',
    version=":versiontools:launch_control_tool:__version__",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    packages=find_packages(),
    description="Command line utility for Launch Control",
    url='https://launchpad.net/launch-control-tool',
    test_suite='launch_control_tool.tests.test_suite',
    license="LGPLv3",
    entry_points="""
    [console_scripts]
    lc-tool=launch_control_tool.main:main
    [launch_control_tool.commands]
    backup=launch_control_tool.commands:backup
    bundles=launch_control_tool.commands:bundles
    data_views=launch_control_tool.commands:data_views
    deserialize=launch_control_tool.commands:deserialize
    get=launch_control_tool.commands:get
    make_stream=launch_control_tool.commands:make_stream
    pull=launch_control_tool.commands:pull
    put=launch_control_tool.commands:put
    query_data_view=launch_control_tool.commands:query_data_view
    restore=launch_control_tool.commands:restore
    server_version=launch_control_tool.commands:server_version
    streams=launch_control_tool.commands:streams
    version=launch_control_tool.commands:version
    """,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        ("License :: OSI Approved :: GNU Library or Lesser General Public"
         " License (LGPL)"),
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Testing"],
    install_requires=[
        'lava-tool >= 0.1',
        'versiontools >= 1.3.1'],
    setup_requires=['versiontools >= 1.3.1'],
    tests_require=[],
    zip_safe=True)
