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

"""
Simple integration for Django settings.py
"""

from django_debian.secret_key import get_secret_key
from django_debian.dbconfig import get_database


class Settings(object):
    """
    Settings object for better integration with Django and Debian.

    Available properties:

        default_database
        SECRET_KEY

    Example usage (inside your settings.py):

        from django_debian.settings import Settings

        DEBIAN_SETTINGS = Settings("yourappname")
        DATABASES = {"default": DEBIAN_SETTINGS.default_database}
        SECRET_KEY = DEBIAN_SETTINGS.SECRET_KEY
    """

    SETTINGS_TEMPLATE = "/etc/{appname}/{filename}.conf"

    def __init__(self, appname, template=None):
        if template is None:
            template = self.SETTINGS_TEMPLATE
        self.appname = appname
        pathname = template.format(appname=self.appname, filename="secret_key")
        self.SECRET_KEY = get_secret_key(pathname)
        pathname = template.format(appname=self.appname, filename="default_database")
        self.default_database = get_database(pathname)
