import mongoengine

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
DATABASES = {}

MONGO_HOSTNAME = 'localhost'
MONGO_DATABASE = 'docbucket'
MONGO_USERNAME = 'docbucket'
MONGO_PASSWORD = 'secret'

mongoengine.connect(MONGO_DATABASE, host=MONGO_HOSTNAME, 
                    username=MONGO_USERNAME, password=MONGO_PASSWORD)

TIME_ZONE = 'Europe/Paris'
LANGUAGE_CODE = 'en-us'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
MEDIA_ROOT = '/usr/local/lib/python2.6/dist-packages/docbucket/media'
MEDIA_URL = '/media/'
ADMIN_MEDIA_PREFIX = '/adm-media/'
SECRET_KEY = '<changeme>'

TEMPLATE_LOADERS = (
	'django.template.loaders.filesystem.Loader',
	'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
	'django.middleware.common.CommonMiddleware',
	'django.contrib.sessions.middleware.SessionMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = ()

TEMPLATE_CONTEXT_PROCESSORS = (
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
)

INSTALLED_APPS = ('docbucket',)

INCOMING_DIRECTORY = '<edit me>'
INCOMING_EXTS = ('.tiff',)

HOCR_CMD = '/usr/bin/cuneiform -l fra -f hocr -o %(output)s %(input)s'
TEXT_CMD = '/usr/bin/cuneiform -l fra -f text -o %(output)s %(input)s'
HOCR2PDF_CMD = '/usr/bin/hocr2pdf -i %(input_img)s -o %(output)s < %(input_hocr)s'
ASSEMBLE_CMD = '/usr/bin/gs -dBATCH -dNOPAUSE -q -sDEVICE=pdfwrite -sOutputFile=%(output)s %(inputs)s'

THUMBNAILS_SIZES = {
	'small': (50, 80),
	'large': (315, 445),
}

WHOOSH_INDEX = '<edit me>'
