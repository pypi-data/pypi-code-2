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
from django.conf import settings
from django.db import connections


class BasePgManager(models.Manager):
    
    PGMANAGER_DB_ALIAS = 'postgresql_manager_conn'
    
    def execute_custom_query(self, sql):
        connection = connections[self.PGMANAGER_DB_ALIAS]
        cursor = connection.cursor()
        cursor.execute(sql)


class PgUserManager(BasePgManager):
    
    def create_role(self, rolename, password, attrs=''):
        adminrole = settings.DATABASES[self.PGMANAGER_DB_ALIAS]['USER']
        self.execute_custom_query(
            "CREATE ROLE %(rolename)s WITH %(attrs)s PASSWORD '%(password)s';" % {
                'rolename': rolename, 'password': password, 'attrs': attrs})
        # Make the admin role member of the new role
        self.execute_custom_query("GRANT %(rolename)s TO %(adminrole)s" % {
            'rolename': rolename, 'adminrole': adminrole})
    
    def drop_role(self, rolename):
        self.execute_custom_query("DROP ROLE %s" % rolename)
    
    def change_password(self, rolename, password):
        self.execute_custom_query(
            "ALTER ROLE %(rolename)s WITH PASSWORD '%(password)s'" % {
                'rolename': rolename, 'password': password})
    
    def rename_role(self, old_name, new_name):
        self.execute_custom_query(
            "ALTER ROLE %(old_name)s RENAME TO %(new_name)s" % {
                'old_name': old_name, 'new_name': new_name})
    
    def limit_connections(self, rolename, connlimit):
        self.execute_custom_query(
            "ALTER ROLE %(rolename)s WITH CONNECTION LIMIT %(connlimit)s" % {
                'rolename': rolename, 'connlimit': connlimit})
    
    def lock_unlock_role(self, rolename, is_active):
        login_attr = 'LOGIN'
        if not is_active:
            login_attr = 'NOLOGIN'
        self.execute_custom_query(
            "ALTER ROLE %(rolename)s WITH %(login_attr)s" % {
                'rolename': rolename, 'login_attr': login_attr})
    


class PgDatabaseManager(BasePgManager):
    
    def create_database(self, database, rolename):
        self.execute_custom_query(
            "CREATE DATABASE %(database)s OWNER %(rolename)s" % {
                'database': database, 'rolename': rolename})
    
    def drop_database(self, database):
        self.execute_custom_query("DROP DATABASE %s" % database)
    
    def rename_database(self, old_name, new_name):
        self.execute_custom_query(
            "ALTER DATABASE %(old_name)s RENAME TO %(new_name)s" % {
                'old_name': old_name, 'new_name': new_name})
    
    def set_owner(self, database, rolename):
        self.execute_custom_query(
            "ALTER DATABASE %(database)s OWNER TO %(rolename)s" % {
                'database': database, 'rolename': rolename})
    
    def limit_connections(self, database, connlimit):
        self.execute_custom_query(
            "ALTER DATABASE %(database)s WITH CONNECTION LIMIT %(connlimit)s" % {
                'database': database, 'connlimit': connlimit})
    

