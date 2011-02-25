import django
import os

def get_amedia_dir():
    return os.path.join(django.__path__[0], 'contrib', 'admin', 'media')
    