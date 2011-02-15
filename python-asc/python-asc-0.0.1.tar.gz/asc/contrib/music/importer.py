from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from asc.parser import Parser

class Importer(object):
    def __init__(self):
        try:
            self.url = settings.ASC_URL
        except AttributeError:
            raise ImproperlyConfigured('No ASC_URL setting found.')

    def run(self):
        return Parser(self.url).tracks
