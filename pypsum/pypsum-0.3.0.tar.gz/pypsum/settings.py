import loremipsum
import os

application_location = os.environ.get('pypsum_location', 'localhost:5000')
client_accepts = os.environ.get('pypsum_accepts', 'application/json')

# Default settings
NAME = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
WORDS_CAPACITY = 50
SENTENCES_CAPACITY = 10
PARAGRAPHS_CAPACITY = 5
DEBUG = False
TESTING = False
PROPAGATE_EXCEPTIONS = False
PRESERVE_CONTEXT_ON_EXCEPTION = True
SECRET_KEY = ''
SESSION_COOKIE_NAME = NAME
PERMANENT_SESSION_LIFETIME = 0
USE_X_SENDFILE = False
LOGGER_NAME = NAME
SERVER_NAME = application_location
MAX_CONTENT_LENGTH = 0
GENERATOR = loremipsum.Generator()

# Specialized settings objects
class Testing(object):
    TESTING = True

class Debug(Testing):
    DEBUG = True

class AppSpot(object):
    SERVER_NAME = 'pypsum.appspot.com'

