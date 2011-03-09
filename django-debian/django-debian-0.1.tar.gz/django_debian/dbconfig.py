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
dbconfig-common integration for django
"""

import re


class ConfigFile(object):
    """
    Configuration file parser compatible with dbconfig-common
    """

    _pattern = re.compile("^(?P<key>[a-zA-Z0-9_]+)='(?P<value>[^']*)'$")

    @classmethod
    def load(cls, appname):
        """
        Load file from /etc/dbconfig-common/APPNAME.conf and store all the
        values that start with dbc_ as instance attributes
        """
        pathname = "/etc/dbconfig-common/%s.conf" % appname
        self = cls()
        for key, value in cls._parse(pathname):
            if key.startswith("dbc_"):
                setattr(self, key, value)

    @classmethod
    def _parse(cls, pathname):
        with open(pathname, "rt") as stream:
            for lineno, line in enumerate(stream, start=1):
                # Strip trailing comments
                if "#" in line:
                    line = line[:line.rindex("#")]
                line = line.strip()
                if line == "":
                    continue
                match = cls._pattern.match(line)
                if match is None:
                    raise ValueError("%s:%d Non a key=value pair!" % (pathname, lineno))
                yield match.group("key"), match.group("value")


def database(appname):
    """
    Get django database settings for dbconfig-common application appname.
    """
    config = ConfigFile.load(appname)
    if config.dbc_dbtype == "sqlite3":
        ENGINE = "django.db.backends.sqlite3"
        NAME = os.path.join(config.dbc_basepath, config.dbc_dbname)
    else:
        # TODO: add support for 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        raise ValueError("Unupported value for dbc_dbtype: %r" % dbc_dbtype)
    return {
        'ENGINE': ENGINE,
        'NAME': NAME, 
        'USER': config.dbc_dbuser, 
        'PASSWORD': config.dbc_dbpass,
        'HOST': config.dbc_dbserver,
        'PORT': config.dbc_dbport
    }
