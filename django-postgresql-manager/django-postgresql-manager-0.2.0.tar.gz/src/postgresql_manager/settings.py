# -*- coding: utf-8 -*-
#
#  This file is part of django-postgresql-manager.
#
#  django-postgresql-manager is a Django based management interface for PostgreSQL users and databases.
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

from django.conf import settings


_PGMANAGER_FORBIDDEN_USER_NAMES = (
    'postgres',
    'postgresql',
    'pg',
    'admin',
    'administrator',
    'root',
    'sys',
    'system',
    )
PGMANAGER_FORBIDDEN_USER_NAMES = getattr(settings, 'PGMANAGER_FORBIDDEN_USER_NAMES', _PGMANAGER_FORBIDDEN_USER_NAMES)

_PGMANAGER_FORBIDDEN_DATABASE_NAMES = (
    'postgres',
    'template0',
    'template1',
    'globals',
    )
PGMANAGER_FORBIDDEN_DATABASE_NAMES = getattr(settings, 'PGMANAGER_FORBIDDEN_DATABASE_NAMES', _PGMANAGER_FORBIDDEN_DATABASE_NAMES)

