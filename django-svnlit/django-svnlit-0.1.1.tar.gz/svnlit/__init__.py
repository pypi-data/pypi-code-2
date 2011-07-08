from django.conf import settings


if not hasattr(settings, 'SVNLIT_CLIENT_TIMEOUT'):
    settings.SVNLIT_CLIENT_TIMEOUT = 20

if not hasattr(settings, 'SVNLIT_CACHE_TIMEOUT'):
    settings.SVNLIT_CACHE_TIMEOUT = 60 * 60 * 24

if not hasattr(settings, 'SVNLIT_SVN_CONFIG_PATH'):
    settings.SVNLIT_SVN_CONFIG_PATH = None

if not hasattr(settings, 'SVNLIT_CHANGESETS_PER_PAGE'):
    settings.SVNLIT_CHANGESETS_PER_PAGE = 50

if not hasattr(settings, 'SVNLIT_AUTO_SYNC'):
    settings.SVNLIT_AUTO_SYNC = True

if not hasattr(settings, 'SVNLIT_SYNC_INTERVAL'):
    settings.SVNLIT_SYNC_INTERVAL = 60
