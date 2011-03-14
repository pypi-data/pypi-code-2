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
    version="0.4",
    description='Debian integration for Django applications',
    author='Zygmunt Krynicki',
    author_email='zygmunt.krynicki@canonical.com',
    url='http://launchpad.net/django-debian',
    long_description="""
    Creating proper Debian packages for even most simple Django
    applications is not easy.
    
    This package provides integration for the following aspcts:
    
    * loading database settings from config file generated with dbconfig-common
    * loading and generating SECRET_KEY
    * integration with django-staticfiles (via maintainer scripts)
    * initial placement and configuration of important directories (via maintainer scripts)
    """,
    packages=find_packages(),
    install_requires=["distribute"],
    data_files=[
        ('/usr/share/django-debian/dpkg/', [
            'dpkg/common',
            'dpkg/config',
            'dpkg/postinst',
            'dpkg/postrm',
            'dpkg/prerm',
        ]),
    ],
    license="LGPL3",
    zip_safe=True,
)
