"""Functions related to generating a simulated settings file.
"""

import os
import os.path
import sys
import string
from random import choice
from copy import deepcopy
import unittest
import logging
logger = logging.getLogger(__name__)


from utils import app_module_name_to_dir
from archive_handlers import create_handler, validate_archive_files
from find_module import find_python_module
from errors import FileMissingError

###### Constants ##########
INSTALL_PATH="install_path"
ADMIN_NAME="admin_name"
ADMIN_EMAIL="admin_email"
SECRET_KEY="secret_key"
DATABASE_ENGINE="database_engine"
DATABASE_NAME="database_name"
DATABASE_USER="database_user"
DATABASE_PASSWORD="database_password"
DATABASE_HOST="database_host"
DATABASE_PORT="database_port"
HOSTNAME="hostname"
PRIVATE_IP_ADDRESS="private_ip_address"
PORT="port"
LOG_DIRECTORY="log_directory"
TIME_ZONE="time_zone"
EMAIL_HOST="email_host"
EMAIL_HOST_USER="email_host_user"
EMAIL_FROM="email_from"
EMAIL_HOST_PASSWORD="email_host_password"
EMAIL_PORT="email_port"


################# Start of engage_settings.py template ##############
engage_settings_template = """
# Auto-generated settings values for django

import sys
import os.path
import urlparse

# additional configuration properties exposed by the django driver
ENGAGE_APP_FILES_BASE = '${install_path}'
ENGAGE_WEBSERVER_HOSTNAME = '${hostname}'
ENGAGE_WEBSERVER_PORT = '${port}'
ENGAGE_LOG_DIRECTORY = '${log_directory}'
ENGAGE_PRIVATE_IP_ADDRESS = ${private_ip_address}

if len(sys.argv[0])>0:
    _log_base_name = os.path.basename(sys.argv[0]).replace(".py","")
else:
    _log_base_name = os.path.basename(sys.executable)
if ((_log_base_name=="django-admin") or (_log_base_name=="manage")) and len(sys.argv)>1:
    _log_base_name = _log_base_name + "-" + sys.argv[1]
ENGAGE_LOG_FILE = os.path.join('${log_directory}', '%s.log' % _log_base_name)

# Engage values for Django standard settings
ADMINS = (('${admin_name}', '${admin_email}'),)
DATABASES = {
    'default': {
        'ENGINE' :  '${database_engine}',  # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME' :  '${database_name}',            # Or path to database file if using sqlite3.
        'USER' : '${database_user}',          # Not used with sqlite3.
        'PASSWORD' : '${database_password}',        # Not used with sqlite3.
        'HOST' : '${database_host}',            # Set to empty string for localhost. Not used with sqlite3.
        'PORT' : '${database_port}',            # Set to empty string for default. Not used with sqlite3.
    }
}
TIME_ZONE = '${time_zone}'
SECRET_KEY = '${secret_key}'

import logging
import logging.handlers
def log_setup_fn(dummy):
    root_logger = logging.getLogger()
    if not os.path.exists(ENGAGE_LOG_DIRECTORY):
        os.makedirs(ENGAGE_LOG_DIRECTORY)
    handler = logging.handlers.RotatingFileHandler(ENGAGE_LOG_FILE, maxBytes=1000000, backupCount=5)
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    handler.setLevel(logging.INFO)            

def dummy_log_setup(dummy):
    pass

LOGGING_CONFIG = '${_logging_fn}'
LOGGING = None


# The following settings are not yet configurable through the website, but
# will eventually be added.
EMAIL_HOST = '${email_host}'
EMAIL_HOST_USER = '${email_host_user}'
EMAIL_FROM = '${email_from}'
EMAIL_HOST_PASSWORD = '${email_host_password}'
EMAIL_PORT = '${email_port}'

# _resolve_name() and import_module() are taken from django.utils.importlib.
# We include them here to enable simulation of the future logging functionality.
# Can remove when we upgrade to the next version of django.
import sys
def _resolve_name(name, package, level):
    if not hasattr(package, 'rindex'):
        raise ValueError("'package' not set to a string")
    dot = len(package)
    for x in xrange(level, 1, -1):
        try:
            dot = package.rindex('.', 0, dot)
        except ValueError:
            raise ValueError("attempted relative import beyond top-level "
                              "package")
    return "%s.%s" % (package[:dot], name)


def import_module(name, package=None):
    if name.startswith('.'):
        if not package:
            raise TypeError("relative imports require the 'package' argument")
        level = 0
        for character in name:
            if character != '.':
                break
            level += 1
        name = _resolve_name(name[level:], package, level)
    __import__(name)
    return sys.modules[name]

def fixup_url(url, ensure_trailing_slash=False):
    sr = urlparse.urlsplit(url)
    if sr[0]=='' and sr[1]=='':
        proto = ''
        netloc = ''
    else:
        proto = 'http'
        if ENGAGE_WEBSERVER_PORT == '80':
            netloc = ENGAGE_WEBSERVER_HOSTNAME
        else:
            netloc = ENGAGE_WEBSERVER_HOSTNAME + ':' + ENGAGE_WEBSERVER_PORT
    if ensure_trailing_slash and (sr[2]!='') and (sr[2][len(sr[2])-1]!='/'):
        path = sr[2] + '/'
    else:
        path = sr[2]
    return urlparse.urlunsplit((proto, netloc, path, sr[3], sr[4]))

"""
################# End of engage_settings.py template ##############

################# Start of deployed_settings.py ##############
deployed_settings_template="""
from ${django_settings_module} import *
_symbols = set(dir())
import ${engage_settings_module} as engage_settings

# the standard django settings that Engage will change at deployment time
if "TIME_ZONE_OVERRIDE" not in _symbols:
    TIME_ZONE = engage_settings.TIME_ZONE

if "SECRET_KEY_OVERRIDE" not in _symbols:
    SECRET_KEY = engage_settings.SECRET_KEY

if "DATABASES_OVERRIDE" not in _symbols:
    DATABASES = engage_settings.DATABASES

if "ADMINS_OVERRIDE" not in _symbols:
    ADMINS = engage_settings.ADMINS

if "LOGGING_OVERRIDE" not in _symbols:
    LOGGING = engage_settings.LOGGING

if "LOGGING_CONFIG_OVERRIDE" not in _symbols:
    LOGGING_CONFIG = engage_settings.LOGGING_CONFIG

# settings that can reference an absolute URL may need to be adjusted.
if ('MEDIA_URL' in _symbols) and (MEDIA_URL != ''):
    MEDIA_URL = engage_settings.fixup_url(MEDIA_URL, True)
if ('ADMIN_MEDIA_PREFIX' in _symbols) and (ADMIN_MEDIA_PREFIX != ''):
    ADMIN_MEDIA_PREFIX = engage_settings.fixup_url(ADMIN_MEDIA_PREFIX, True)

# logging config support not yet in released django,
# so we call it explicitly. This is similar to the latest code
# in django/config/__init__.py
if LOGGING_CONFIG:
    _logging_config_path, _logging_config_func_name = LOGGING_CONFIG.rsplit('.', 1)
    _logging_config_module = engage_settings.import_module(_logging_config_path)
    _logging_config_func = getattr(_logging_config_module, _logging_config_func_name)
    _logging_config_func(LOGGING)
"""
################# End of deployed_settings.py ##############


def _gen_rand_string(length, chars=string.letters+string.digits):
    return ''.join([ choice(chars) for i in range(length) ])


def generate_settings_file(app_dir_path, django_settings_module, properties=None):
    """Generate the engage_settings.py and deployed_settings.py files. Returns a
    list of operations which will put the files back to their original state,
    where each operation is a (function, arglist) tuple.
    """
    undo_ops = []
    # first, get the location of the python path.
    python_path = find_python_module(django_settings_module, app_dir_path)
    if not python_path:
        raise FileMissingError("Cannot find django settings module %s under %s" %
                               (django_settings_module, app_dir_path))

    # compute the paths for the engage_settings.py and deployed_settings.py modules
    subdirs = django_settings_module.split('.')
    if len(subdirs)==1:
        parent_dir = python_path
        engage_settings_module = "engage_settings"
        deployed_settings_module = "deployed_settings"
    else:
        parent_dir = os.path.join(python_path, "/".join(subdirs[0:-1]))
        parent_module = ".".join(subdirs[0:-1])
        engage_settings_module = parent_module + ".engage_settings"
        deployed_settings_module = parent_module + "deployed_settings"
        
    assert os.path.exists(parent_dir), "Internal error: could not find directory %s" % parent_dir
    engage_settings_py = os.path.join(parent_dir, "engage_settings.py")
    deployed_settings_py = os.path.join(parent_dir, "deployed_settings.py")
        

    # warn if the generated files already exist
    if os.path.exists(engage_settings_py):
        logger.warn("%s already exists, will be overwritten" % engage_settings_py)
    if os.path.exists(deployed_settings_py):
        logger.warn("%s already exists, will be overwritten" % deployed_settings_py)
        
    # now generate the engage settings file
    if not properties:
        properties = {
            INSTALL_PATH: os.path.dirname(app_dir_path),
            ADMIN_NAME: "admin_" + _gen_rand_string(5),
            ADMIN_EMAIL: "admn" + _gen_rand_string(5) + "@foo.com",
            SECRET_KEY: _gen_rand_string(50, chars=string.digits+string.letters+"!#%&()*+,-./:;<=>?@[]^_`{|}~"),
            DATABASE_ENGINE: 'django.db.backends.sqlite3',
            DATABASE_NAME: os.path.join(os.path.join(parent_dir, "db"), "django.db"),
            DATABASE_USER: '',
            DATABASE_PASSWORD: '',
            DATABASE_HOST: '',
            DATABASE_PORT: '',
            HOSTNAME: "localhost",
            PRIVATE_IP_ADDRESS: None,
            PORT: 8000,
            LOG_DIRECTORY: os.path.join(app_dir_path, "log"),
            TIME_ZONE: _gen_rand_string(8),
            EMAIL_HOST: 'bar.com',
            EMAIL_HOST_USER: "admin",
            EMAIL_FROM: 'admin@bar.com',
            EMAIL_HOST_PASSWORD: _gen_rand_string(6),
            EMAIL_PORT: 25,
            "_logging_fn": "%s.dummy_log_setup" % \
                           engage_settings_module
        }
    else:
        properties = deepcopy(properties)
        properties["_logging_fn"] = "%s.log_setup_fn" % \
                                    engage_settings_module
    template = string.Template(engage_settings_template)
    result = template.substitute(properties)
    with open(engage_settings_py, "wb") as f:
        f.write(result)
    undo_ops.insert(0, (os.remove, [engage_settings_py]))

    # now generate the deployed_settings.py file
    template = string.Template(deployed_settings_template)
    result = template.substitute({"django_settings_module": django_settings_module,
                                  "engage_settings_module": engage_settings_module})
    with open(deployed_settings_py, "wb") as f:
        f.write(result)
    undo_ops.insert(0, (os.remove, [deployed_settings_py]))
    return undo_ops


def simulated_install(archive_file, install_path, django_settings_module):
    """Simulate the install process. install_path is the directory under
    which we extract the archive.
    """
    with create_handler(archive_file) as h:
        common_dir = validate_archive_files(h.get_namelist())
        h.extract(install_path)
    app_dir_path = os.path.join(install_path, common_dir)
    undo_ops = generate_settings_file(app_dir_path, django_settings_module)
    return (app_dir_path, undo_ops)
    

class TestGenerateSettings(unittest.TestCase):
    """Unit tests for the generate_settings function.
    """
    def _make_py_file(self, parent_dir, name, contents="# \n"):
        with open(os.path.join(parent_dir, name), "w") as f:
            f.write(contents)

    def setUp(self):
        """We set up a sample application directory layout in a temp directory.
        This temp directory is deleted in the tearDown method so that we don't
        leave a mess around.
        """
        import tempfile
        self.temp_dir = tempfile.mkdtemp()
        self.app_dir_path = os.path.join(self.temp_dir, "app_dir")
        os.mkdir(self.app_dir_path)
        self.settings_file_dir = os.path.join(self.app_dir_path, "settings_file_dir")
        os.mkdir(self.settings_file_dir)
        self._make_py_file(self.settings_file_dir, "__init__.py")
        self._make_py_file(self.settings_file_dir, "settings.py")
        self.django_settings_module = "settings_file_dir.settings"
        self.saved_sys_path = sys.path

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
        sys.path = self.saved_sys_path

    def assertFileExists(self, filepath):
        self.assertTrue(os.path.exists(filepath), "%s is missing" % filepath)

    def assertModuleHasSetting(self, module, setting):
        self.assertTrue(hasattr(module, setting), "Module missing setting %s" % setting)

    def test_generate_settings(self):
        ops = generate_settings_file(self.app_dir_path, self.django_settings_module)
        self.assertFileExists(os.path.join(self.settings_file_dir, "engage_settings.py"))
        self.assertFileExists(os.path.join(self.settings_file_dir, "deployed_settings.py"))
        sys.path = [self.app_dir_path] + sys.path
        settings_module = __import__("settings_file_dir.deployed_settings")
        self.assertModuleHasSetting(settings_module.deployed_settings, "DATABASES")

if __name__ == '__main__':
    unittest.main()
