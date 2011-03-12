from __future__ import absolute_import
from fabric.api import *
from fabtest import fab
from fab_deploy.mysql import mysql_install, _mysql_is_installed, mysql_create_db, mysql_execute
from .base import FabDeployTest

def mysql_is_installed():
    return fab(_mysql_is_installed)[0]

def database_exists(db_name):
    databases = fab(mysql_execute, 'show databases;')[0].splitlines()
    return db_name in databases

class MysqlTest(FabDeployTest):
    host = 'root@127.0.0.1:2222'

    def setup_conf(self):
        super(MysqlTest, self).setup_conf()
        env.conf['DB_PASSWORD'] = '123'
        env.conf['DB_NAME'] = 'new_database'

    def test_mysql(self):
        self.assertFalse(mysql_is_installed())

        fab(mysql_install)
        self.assertTrue(mysql_is_installed())

        self.assertFalse(database_exists('new_database'))
        fab(mysql_create_db)
        self.assertTrue(database_exists('new_database'))

