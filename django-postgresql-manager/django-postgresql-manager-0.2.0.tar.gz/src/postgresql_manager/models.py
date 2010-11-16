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


from django.db import models
from django.db.models import signals

from postgresql_manager import signal_cb
from postgresql_manager import managers



class PgUser(models.Model):
    
    name = models.SlugField(verbose_name='name', max_length=55, db_index=True, unique=True, help_text='''Enter a name for the PostgreSQL cluster user''')
    connlimit = models.IntegerField(verbose_name='connection limit', default=-1, help_text='''If the user is active, this specifies how many concurrent connections this user can make to the server. -1 (the default) means no limit.''')
    is_active = models.BooleanField(verbose_name='active', default=True, db_index=True, help_text='''Mark the user as active or not. A user that is marked as inactive cannot login to the PostgreSQL cluster.''')

    date_created = models.DateTimeField(verbose_name='created on', auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='last modified on', auto_now=True)
    created_by = models.ForeignKey('auth.User', related_name='%(class)s_created_by')
    
    objects = managers.PgUserManager()
    
    class Meta:
        verbose_name = 'PostgreSQL User'
        verbose_name_plural = 'PostgreSQL Users'
    
    def __unicode__(self):
        return self.name

signals.pre_delete.connect(signal_cb.dbms_drop_role, sender=PgUser)



class PgDatabase(models.Model):
    
    name = models.SlugField(verbose_name='name', max_length=100, db_index=True, unique=True, help_text='''Enter a name for the PostgreSQL database.''')
    owner = models.ForeignKey('postgresql_manager.PgUser', related_name='%(class)s_owner', help_text='''Select an owner for this database.''')
    connlimit = models.IntegerField(verbose_name='connection limit', default=-1, help_text='''Enter the number of concurrent connections that can be made to this database. -1 (the default) means no limit.''')
    
    date_created = models.DateTimeField(verbose_name='created on', auto_now_add=True)
    date_modified = models.DateTimeField(verbose_name='last modified on', auto_now=True)
    created_by = models.ForeignKey('auth.User', related_name='%(class)s_created_by')
    
    objects = managers.PgDatabaseManager()
    
    class Meta:
        verbose_name = 'PostgreSQL Database'
        verbose_name_plural = 'PostgreSQL Databases'

    def __unicode__(self):
        return self.name

signals.pre_delete.connect(signal_cb.dbms_drop_database, sender=PgDatabase)

