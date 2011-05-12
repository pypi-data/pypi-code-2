try:
    from ZPublisher.Iterators import filestream_iterator
    HAS_ITERATOR = True
except ImportError:
    HAS_ITERATOR = False

PROJECTNAME = 'ExternalStorage'

GLOBALS = globals()

SKINS_DIR = 'skins'

ARCHIVE_PREFIX = '_ARCHIVE'
ENVIRONMENT_VARIABLE = 'EXTERNAL_STORAGE_BASE_PATH'
