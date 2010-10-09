ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Detriot'

DATABASES = {
    'default': {
        'NAME': 'laptop_mousedb', # Or path to database file if using sqlite3.
        'ENGINE': 'django.db.backends.mysql', #  Choose one of 'django.db.backends.postgresql_psycopg2','django.db.backends.postgresql', 'django.db.backends.mysql', 'django.db.backends.sqlite3', 'django.db.backends.oracle'
        'USER': 'root',  # Not used with sqlite3.
        'PASSWORD': 'password', # Not used with sqlite3
	'HOST':'', # Set to empty string for localhost. Not used with sqlite3.
	'PORT':'', # Set to empty string for default. Not used with sqlite3.
    }
}

