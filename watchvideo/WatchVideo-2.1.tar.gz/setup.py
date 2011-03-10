#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2010  Michał Masłowski  <mtjm@mtjm.eu>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
Script used to install WatchVideo.
"""


from setuptools import setup, find_packages


setup(
    name="WatchVideo",
    version="2.1",
    author="Leonardo Gastón De Luca",
    author_email="leo@kde.org.ar",
    url="http://qt-apps.org/content/show.php/WatchVideo?content=128368",
    download_url="http://download.savannah.gnu.org/releases/watchvideo/",
    packages=find_packages(),
    description="A small application to play or download videos " \
        "from various YouTube-like sites.",
    long_description=open("README.txt").read(),
    license="GNU Affero General Public License v3 or later",
    install_requires=(
        "GetMediumURL >= 0.0a2dev",
        ),
    entry_points = {
        'console_scripts': 'watchvideo = watchvideo.watchvideo_cli:run',
        'gui_scripts': 'qtwatchvideo = watchvideo.watchvideo_gui:run',
        },
    classifiers=(
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        ),
    use_2to3=True,
    zip_safe=True,
    test_suite="tests_watchvideo.__init__",
    )
