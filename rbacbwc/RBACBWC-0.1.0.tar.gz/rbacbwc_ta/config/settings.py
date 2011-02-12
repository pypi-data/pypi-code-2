import logging
from os import path

from blazeweb.config import DefaultSettings

basedir = path.dirname(path.dirname(__file__))
app_package = path.basename(basedir)

class Default(DefaultSettings):
    def init(self):
        self.dirs.base = basedir
        self.app_package = app_package
        DefaultSettings.init(self)

        self.add_component(app_package, 'rbac', 'rbacbwc')
        self.add_component(app_package, 'sqlalchemy', 'sqlalchemybwc')

class Test(Default):
    def init(self):
        Default.init(self)
        self.apply_test_settings()

        # database
        self.db.url = 'sqlite://'

try:
    from site_settings import *
except ImportError, e:
    if 'No module named site_settings' not in str(e):
        raise
