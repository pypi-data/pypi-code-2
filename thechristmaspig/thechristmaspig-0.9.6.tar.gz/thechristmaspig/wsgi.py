import os
from django.core import management
 
def main(settings_file):
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_file
    from django.core.handlers.wsgi import WSGIHandler
    return WSGIHandler()
