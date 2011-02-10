from django import template
from django.conf import settings
from fresh_media.hash_methods import get_token

import os.path
import urlparse

register = template.Library()


@register.simple_tag
def media(filename):
    path = os.path.join(settings.MEDIA_ROOT, filename)
    token = get_token(path)
    url = urlparse.urljoin(settings.MEDIA_URL, "%s?%s" % (filename, token))
    return url
