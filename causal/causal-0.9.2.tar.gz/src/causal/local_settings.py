DEBUG = True
ENABLE_ADMIN = True
ENABLE_ADMIN_DOCS = True
SERVE_STATIC = True
USE_GOOGLE_CDN = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': '/Users/wesleymason/causal.db',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

ENABLE_CACHING = True

ENABLE_REGISTRATION = True

INSTALLED_SERVICES = (
    'causal.twitter',
#    'causal.foursquare',
    'causal.flickr',
    'causal.facebook',
    'causal.github',
    'causal.lastfm',
)

SECRET_KEY = '`|9IK8w@VfU&([H{vaKpTRsmFq]zw7&pTIK4h#A$`@*>(&xSn<N(dg?=sxD|;*D'
