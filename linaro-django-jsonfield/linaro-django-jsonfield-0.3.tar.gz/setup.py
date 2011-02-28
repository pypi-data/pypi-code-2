#!/usr/bin/env python
# Copyright (C) 2010 Linaro Limited
#
# Author: Zygmunt Krynicki <zygmunt.krynicki@linaro.org>
#
# This file is part of linaro-django-jsonfield.
#
# linaro-django-jsonfield is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation
#
# linaro-django-jsonfield is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with linaro-django-jsonfield.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup

setup(
    name = 'linaro-django-jsonfield',
    version = "0.3",
    author = "Zygmunt Krynicki",
    author_email = "zygmunt.krynicki@linaro.org",
    description = "Django's missing JSON field similar to XMLField",
    url = 'https://launchpad.net/django-jsonfield',
    keywords = ['django', 'json', 'field'],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
    ],
    license = "LGPLv3",
    zip_safe = True,
    packages = [
        'linaro_django_jsonfield',
    ],
    install_requires=[
        'Django >= 1.0',
    ],
)
