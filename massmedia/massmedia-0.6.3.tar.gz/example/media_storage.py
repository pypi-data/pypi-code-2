from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

DEFAULT_ROOT = os.path.join(os.path.dirname(__file__), 'store_here')
DEFAULT_URL = '/mymedia/'

class MediaStorage(FileSystemStorage):
    def __init__(self, location='', base_url='', *args, **kwargs):
        real_location = os.path.join(DEFAULT_ROOT, location)
        real_base_url = DEFAULT_URL + base_url
        super(MediaStorage, self).__init__(real_location, real_base_url, *args, **kwargs)
