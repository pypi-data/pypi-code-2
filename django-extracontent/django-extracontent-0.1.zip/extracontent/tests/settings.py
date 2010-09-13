DEFAULT_CHARSET = 'utf-8'
 
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = ':memory:'
 
ROOT_URLCONF = 'settings'

INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'extracontent',
    'extracontent.tests'
)
 
TEMPLATE_LOADERS = (
    'django.template.loaders.app_directories.load_template_source',
)
 

