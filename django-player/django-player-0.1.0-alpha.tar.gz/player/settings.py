from os import path

PLAYERDIR = path.dirname(path.abspath(__file__))

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'pagination.middleware.PaginationMiddleware',
    'player.multimedia.middleware.MediaMiddleware',
    'player.block.middleware.RenderBlockMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'dbtemplates.loader.Loader',
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'django.template.loaders.eggs.Loader',
)

TEMPLATE_DIRS = (
    path.join(PLAYERDIR, 'templates'),
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # required by django-playerlayer
    'south',
    'sorl.thumbnail',
    'dbtemplates',
    'pagination',
    'inplaceeditform',
    'inlinetrans',
    'johnny',
    'oembed',
    'cmsutils',
    'compressor',
    'announcements',
    'dbresolver',
    'debug_toolbar',
    # django-playerlayer
    'player.base',
    'player.block',
    'player.crawler',
    'player.data',
    'player.dbtemplate',
    'player.dburl',
    'player.logicaldelete',
    'player.multimedia',
    'player.manage',
)

INTERNAL_IPS = ('127.0.0.1', )

SLUG_RE = r'[-_\.\w]+'

LOGIN_URL = '/manage/login/'

LOGOUT_URL = '/manage/logout/'

MEDIA_URL = '/media/'

STATIC_URL = '/static/'

ADMIN_MEDIA_PREFIX = '/static/admin/'

# dbtemplates settings
DBTEMPLATES_USE_CODEMIRROR = True
DBTEMPLATES_MEDIA_PREFIX = STATIC_URL + 'codemirror/'
DBTEMPLATES_AUTO_POPULATE_CONTENT = False
DBTEMPLATES_CACHE_BACKEND = 'dbtemplates.cache.DjangoCacheBackend'

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
