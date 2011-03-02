import os
import sys


# If set, serve this local directory alongside files from the remote package
# index. Directory structure is <MAGNUM_SERVE_PATH>/<package>/<filename>
MAGNUM_SERVE_PATH = None

# Remote packages are cached here. If not set, remote packages won't be
# downloaded.
MAGNUM_CACHE_PATH = None

# URL of the remote package index.
MAGNUM_REMOTE_URL = 'http://pypi.python.org/simple/'

# Cache lifetime of the remote index's list of packages.
MAGNUM_REMOTE_PACKAGE_NAMES_LIFETIME = 60 * 60 * 2

# Cache lifetime of the remote index's list of files for a package.
MAGNUM_REMOTE_DIST_NAMES_LIFETIME = 60 * 60 * 24


sys.path = [
    os.path.join(os.path.dirname(__file__), '../..'),
] + sys.path

DEBUG = True
TEMPLATE_DEBUG = DEBUG

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

ROOT_URLCONF = 'serverproject.urls'

INSTALLED_APPS = (
    'magnum',
)
