import logging
import os
from os.path import join as pjoin
import shlex
import subprocess
import zipfile
from blazeutils.helpers import csvtolist, Timer
from blazeutils.datastructures import OrderedDict

class BaseAction(object):
    
    def __init__(self, batch, settings):
        self.batch = batch
        self.settings = settings
        self.stats = OrderedDict()
        self.timer = Timer()
        self._setup_logging()
    
    def _setup_logging(self):
        cname = self.__class__.__name__
        self.log = logging.getLogger('blazech.actions.%s' % cname)
    
    def execute(self):
        pass
    
    def elapsed_stat(self, name):
        self.stats['elapsed_' + name] = self.timer.elapsed(name)

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
        self.log.vdebug('cmd args: %s', args)
        for arg in args:
            if not isinstance(arg, basestring):
                raise TypeError('arg %s is %s, but needs to be a string' % (arg, type(arg)))
        proc = subprocess.Popen(
                args,
                stdin=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        stdout, stderr = proc.communicate(stdin)
        self.log.debug('cmd return code: %s', proc.returncode)
        self.log.debug('cmd stdout: %s', stdout)
        self.log.debug('cmd stderr: %s', stderr)
        return proc.returncode, stdout, stderr
    
    def execute(self):
        cmd_str = self.settings.cmd
        args = shlex.split(cmd_str)
        self.log.debug('executing: %s', cmd_str)
        self.runcmd(args)      
        
class DatabaseBackupBase(SystemCommand):
    
    @property
    def dbnames(self):
        try:
            touse = csvtolist(self.settings.include)
            self.log.debug('using dbnames from settings.include: %s', touse)
            return touse
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
        return all_db_names
            
    def sql_file_path(self, dbname):
        return pjoin(self.settings.target_dir, dbname + '.sql')
        
    def zip_file_path(self, dbname):
        return pjoin(self.settings.target_dir, dbname + '.zip')

    def perform_compression(self, dbname):
        if self.file_compression == 'zip':
            zipf = zipfile.ZipFile(self.zip_file_path(dbname), "w", zipfile.ZIP_DEFLATED )
            sql_file = self.sql_file_path(dbname)
            zipf.write(sql_file, os.path.basename(sql_file) )
            zipf.close()
            if self.after_compression == 'delete_originals':
                os.unlink(sql_file)
    
    def execute(self):
        self.dbport = getattr(self.settings, 'port', '3306')
        self.file_compression = getattr(self.settings, 'file_compression', 'zip')
        self.after_compression = getattr(self.settings, 'after_compression', 'delete_originals')
        
        self.timer.start('total')
        for dbname in self.dbnames:
            self.log.minimal('backing up db: %s', dbname)
            self.timer.start('backup_db_%s' % dbname)
            resultcode, stdout, stderr = self.perform_backup(dbname)
            self.elapsed_stat('backup_db_%s' % dbname)
            if resultcode == 0:
                self.timer.start('zip_db_%s' % dbname)
                self.perform_compression(dbname)
                self.elapsed_stat('zip_db_%s' % dbname)
            else:
                self.log.minimal('mysqldump command failed for db: %s', dbname)
        self.elapsed_stat('total')
        self.log.info('stats: %s', self.stats)

class MysqlBackup(DatabaseBackupBase):
    
    def fetch_all_dbnames(self):
        self.timer.start('elapsed_list_dbs')
        returncode, stdout, stderr = self.runcmd(self.list_db_args())
        self.elapsed_stat('elapsed_list_dbs')
        
        if returncode != 0:
            self.log.minimal('list databases command failed')
            return tuple()
        
        # the first row is the column header "Databases" so we strip that off
        # then every line is a DB name
        return stdout.split('\n')[1:]
    
    def common_args(self):
        return (
            '-h',
            self.settings.host,
            '-u',
            self.settings.user,
            '-p%s' %  self.settings.password,
            '-P',
            str(self.dbport),
        )
    
    def backup_args(self, dbname):
        return (pjoin(self.settings.bin_path, 'mysqldump'), ) + \
            self.common_args() + \
            (
            '-r',
            self.sql_file_path(dbname),
            dbname
        )
        
    def list_db_args(self):
        return (pjoin(self.settings.bin_path, 'mysql'), ) + \
            self.common_args() + \
            (
            '--batch',
            '-e',
            'show databases'
        )
    
    def perform_backup(self, dbname):
        return self.runcmd(self.backup_args(dbname))
