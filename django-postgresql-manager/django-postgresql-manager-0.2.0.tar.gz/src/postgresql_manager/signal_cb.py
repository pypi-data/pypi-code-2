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

from django.db.models.loading import cache


def dbms_drop_role(sender, **kwargs):
    PgUser = cache.get_model('postgresql_manager', 'PgUser')
    instance = kwargs['instance']
    PgUser.objects.drop_role(instance.name)

    
def dbms_drop_database(sender, **kwargs):
    PgDatabase = cache.get_model('postgresql_manager', 'PgDatabase')
    instance = kwargs['instance']
    PgDatabase.objects.drop_database(instance.name)
