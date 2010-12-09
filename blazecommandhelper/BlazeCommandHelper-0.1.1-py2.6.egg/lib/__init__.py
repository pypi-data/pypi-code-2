import logging
import os
from os.path import join as pjoin
import shlex
import subprocess
import zipfile
from blazeutils.helpers import csvtolist

class BaseAction(object):
    
    def __init__(self, batch, settings):
        self.batch = batch
        self.settings = settings
        
        self._setup_logging()
    
    def _setup_logging(self):
        cname = self.__class__.__name__
        self.log = logging.getLogger('blazech.actions.%s' % cname)
    
    def execute(self):
        pass

class TestUseOnly(BaseAction):
    """ only use this for testing"""

    def execute(self):
        self.log.info('test output')
        
class RaiseException(BaseAction):
    """ only use this for testing"""
    
    def execute(self):
        assert False, 'this is meant for testing'

class SystemCommand(BaseAction):
    
    def runcmd(self, args, stdin=''):
        proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        return proc.communicate(stdin)
    
    def execute(self):
        cmd_str = self.settings.cmd
        args = shlex.split(cmd_str)
        self.log.debug('executing: %s', cmd_str)
        self.log.vdebug('cmd string parsed as: %s' % args)
        stdout, stderr = self.runcmd(args)
        self.log.debug('cmd stdout: %s', stdout)
        self.log.debug('cmd stderr: %s', stderr)       
        
class DatabaseBackupBase(SystemCommand):
    
    @property
    def dbnames(self):
        try:
            touse = csvtolist(self.settings.include)
            self.log.debug('using dbnames from include setting: %s', touse)
        except AttributeError, e:
            if 'no attribute \'include\'' not in str(e):
                raise
        all_db_names = self.fetch_all_dbnames()
        self.log.debug('fetched db names: %s', all_db_names)
        try:
            for dbname in csvtolist(self.settings.exclude):
                all_db_names.remove(dbname)
            self.log.debug('excluded dbnames: %s', self.settings.exclude)
        except AttributeError, e:
            if 'no attribute \'exclude\'' not in str(e):
                raise
            
    def sql_file_path(self, dbname):
        return path.join(self.settings.target_dir, dbname + '.sql')
        
    def zip_file_path(self, dbname):
        return path.join(self.settings.target_dir, dbname + '.zip')

    def perform_compression(self, dbname):
        if self.file_compression == 'zip':
            zipf = zipfile.ZipFile(destinationfile, "w", zipfile.ZIP_DEFLATED )
            sql_file = self.sql_file_path()
            zipf.write(sqlfile, os.path.basename(sql_file) )
            zipf.close()
            if self.after_compression == 'delete_originals':
                os.unlink(sql_file)
    
    def execute(self):
        self.dbport = getattr(self.settings, 'port', 3306)
        self.file_compression = getattr(self.settings, 'file_compression', 'zip')
        self.after_compression = getattr(self.settings, 'after_compression', 'delete_originals')
        
        for dbname in self.dbnames:
            self.perform_backup(dbname)
            self.perform_compression(dbname)

class MysqlBackup(DatabaseBackupBase):
    
    def fetch_all_dbnames(self):
        try:
            import MySQLdb
            db = MySQLdb.connect(
                host=self.settings.host, 
                user=self.settings.user, 
                passwd=self.settings.password, 
                db="mysql", 
                port=self.dbport
            )
        except Exception, e:
            self.log.exception('mysql connection failed: %s', e)
            raise JobError

        cursor = db.cursor()
        cursor.execute("show databases")
        mysql_database_listings = cursor.fetchall()
        cursor.close()
        
        dbnames = []
        for row in mysql_database_listings:
            dbnames.append(row[0])
        
        return dbnames
    
    def cmdargs(self, dbname):
        return (
            pjoin(self.settings.bin_path, 'mysqldump'),
            '-h',
            self.settings.host,
            '-u',
            self.settings.user,
            '-p',
            self.settings.password,
            'r',
            self.sql_file_path(dbname),
            '-P',
            self.dbport,
            dbname
        )
    
    def perform_backup(self, dbname):
        self.runcmd(self.cmdargs(dbname))
