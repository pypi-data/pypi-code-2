from django.template import loader
from uta.loader import BaseLoaderMonkeyPatched

loader.BaseLoader = BaseLoaderMonkeyPatched
