import hashlib

from django.core.cache import cache
from django.template import TemplateDoesNotExist
from django.template.loader import BaseLoader

from magneto import cache_key
from models import Template


class CachedTemplateLoader(BaseLoader):
    is_usable = True
    timeout = 1800

    def load_template_source(self, template_name, template_dirs=None):
        if template_name == "":
            template_name = "index"

        hash = cache_key(template_name)
        content = cache.get(hash)

        if content == "miss":
            raise TemplateDoesNotExist(template_name)

        if content:
            return (content, template_name)

        try:
            template = Template.on_site.get(name=template_name)
            cache.set(hash, template.content, self.timeout)
            return (template.content, template_name)
        except:
            cache.set(hash, "miss")
            raise TemplateDoesNotExist(template_name)
