# -*- coding: utf-8 -*-
#
#  This file is part of django-postgresql-manager.
#
#  django-postgresql-manager - a Django application which can be used to manage
#  PostgreSQL users and databases.
#
#  Development Web Site:
#    - http://www.codetrax.org/projects/django-postgresql-manager
#  Public Source Code Repository:
#    - https://source.codetrax.org/hgroot/django-postgresql-manager
#
#  Copyright 2010 George Notaras <gnot [at] g-loaded.eu>
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

VERSION = (0, 1, 6, 'final', 0)

def get_version():
    version = '%d.%d.%d' % (VERSION[0], VERSION[1], VERSION[2])
    return version


long_description = """
*django-postgresql-manager* is a Django application which can be used to manage
PostgreSQL users and databases using a web interface.

Features
--------
django-postgresql-manager currently supports:

- User (role) creation/deletion/renaming.
- Database creation/deletion/renaming.
- Database ownership changing.
- Control over the connection limit for users and databases.
- Marking a user as not active.
- Multiple PostgreSQL roles and databases per Django user. Each user has
  control over the roles and databases it has created.

The distribution package includes an example project, which can be used to
demonstrate the application quickly.

More information about the installation, configuration and usage of this
application can be found in the *HELP* file inside the distribution package
or in the project's
`wiki <http://www.codetrax.org/projects/django-postgresql-manager/wiki>`_.

In case you run into any problems while using this application it is highly
recommended you file a bug report at the project's
`issue tracker <http://www.codetrax.org/projects/django-postgresql-manager/issues>`_.

"""
