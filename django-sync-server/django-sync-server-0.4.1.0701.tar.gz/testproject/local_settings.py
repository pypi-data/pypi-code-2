# Change normal django stuff, e.g.: the database settings:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'my_weave_data.db3',
    }
}

SECRET_KEY = "Make this unique, and don't share it with anybody!"

# Change django-sync-server app settings:
from weave import app_settings as WEAVE

WEAVE.RECAPTCHA_PUBLIC_KEY = 'Put your public key here'
WEAVE.RECAPTCHA_PRIVATE_KEY = '...and your private key here ;)'

WEAVE.BASICAUTH_REALM = "wave server login"

# Create users without any captcha.
# NOT RECOMMENDED! Spam bots can flooding your server!
WEAVE.DONT_USE_CAPTCHA = True

# Log request/reponse debug information
WEAVE.DEBUG_REQUEST = False
