# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

import os, shutil, sys

from benri.config import Config
from pkg_resources import Requirement, resource_filename

from stellaris.utils import create_logger

class EnvironmentPathNotFound(Exception): pass
class EnvironmentAlreadyExists(Exception): pass
    
class Environment(object):
    
    def __init__(self, path, create = False):
        self.__path = path
        
        if create:
            self.create(self.__path)
            
        if not os.path.exists(self.__path):
            raise EnvironmentPathNotFound(self.__path)

        config_path = os.path.join(self.etc_dir, 'stellaris.cfg')
        self.config = Config(config_path, path)
        
        self.log = self.setup_logging()
    
    @property
    def log_dir(self):
        return os.path.join(self.__path, 'logs')

    @property
    def db_dir(self):
        return os.path.join(self.__path, 'db')

    @property
    def data_dir(self):
        return os.path.join(self.__path, 'data')
        
    @property
    def etc_dir(self):
        return os.path.join(self.__path, 'etc')

    @property
    def static_dir(self):
        return os.path.join(self.__path, 'static')

    @property
    def service_prefix(self):
        return self.config['service']['prefix']
        
    def create(self, path):
        if os.path.exists(path):
            raise EnvironmentAlreadyExists(path)

        dirs = [os.path.join(path, dir_name) for dir_name in [self.db_dir, self.log_dir, self.data_dir]]
        static_dir = resource_filename(Requirement.parse("stellaris"),"stellaris/data/static")
        etc_dir = resource_filename(Requirement.parse("stellaris"),"stellaris/data/etc")
        
        try:
            os.mkdir(path)
            for dir_name in dirs:
                os.mkdir(dir_name)
                
            shutil.copytree(static_dir, self.static_dir)
            shutil.copytree(etc_dir, self.etc_dir)
        except:
            raise

    def migrate(self, version=None):
        static_dir = resource_filename(Requirement.parse("stellaris"), "stellaris/data/static")
        shutil.rmtree(self.static_dir)
        shutil.copytree(static_dir, self.static_dir)

    def setup_logging(self):
        log_level = self.config['logging']['level'].upper() # CRITICAL, ERROR, WARNING, INFO, DEBUG
        log_type = self.config['logging']['type'].lower() # file, console
        log_file = os.path.join(self.log_dir, 'stellaris.log')
        
        return create_logger(log_id='stellaris', log_level=log_level, log_type=log_type, log_file=log_file)
