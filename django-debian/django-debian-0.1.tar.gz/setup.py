#!/usr/bin/python
# Copyright (C) 2011 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of django-debian.
#
# django-debian is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# django-debian is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with django-debian.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages

setup(
    name="django-debian",
    version="0.1",
    description='Debian integration for Django applications',
    author='Zygmunt Krynicki',
    author_email='zygmunt.krynicki@canonical.com',
    url='http://launchpad.net/django-debian',
    packages=find_packages(),
    install_requires=[ "distribute" ],
    license = "LGPL3",
    zip_safe=True,
)
