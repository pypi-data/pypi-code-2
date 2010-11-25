
from pylons import app_globals


class FileUploadMiddleware(object):
    def __init__(self, app, temp_storage=None):
        self.temp_storage = temp_storage
        self.app = app

    def __call__(self, environ, start_response):
        # Do stuff
        return self.app(environ, start_response)

