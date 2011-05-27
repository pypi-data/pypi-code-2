import settings

DEBUG = True if settings.DEBUG else False

# ignore individual pages
# default: ignore 405, 410
try:
    ERRORPAGES_PAGES_IGNORE = settings.ERRORPAGES_PAGES_IGNORE
except:
    ERRORPAGES_PAGES_IGNORE = (405, 410)

# disable all error pages, no matter what
# default: enabled
try:
    ERRORPAGES_PAGES_ENABLED = settings.ERRORPAGES_PAGES_ENABLED
except:
    ERRORPAGES_PAGES_ENABLED = True
