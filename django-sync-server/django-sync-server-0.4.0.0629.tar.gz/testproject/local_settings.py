# Change normal django stuff, e.g.: the database settings:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'my_weave_data.db3',
    }
}



# Change django-sync-server app settings:
from weave import app_settings as WEAVE

# Log request/reponse debug information
#WEAVE.DEBUG_REQUEST = True

# log to stderr
import logging
from weave import Logging

#        import logging
#        logging.basicConfig(level=logging.DEBUG)

logger = Logging.get_logger()
logger.setLevel(logging.DEBUG)
logger.handlers = [logging.StreamHandler()] # setting would be import more than one time

#logging.basicConfig(level=logging.DEBUG)
#logger.basicConfig(level=logging.DEBUG)


WEAVE.DONT_USE_CAPTCHA = True

#
#WEAVE.RECAPTCHA_PUBLIC_KEY = 'Put your public key here'
#WEAVE.RECAPTCHA_PRIVATE_KEY = '...and your private key here ;)'
#
#WEAVE.BASICAUTH_REALM = "wave server login"
