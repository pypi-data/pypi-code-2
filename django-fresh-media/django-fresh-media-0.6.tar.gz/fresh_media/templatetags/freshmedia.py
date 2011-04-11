from django import template
from django.conf import settings
from fresh_media.hash_methods import get_token, FAIL_IF_NON_EXIST

import os.path
import urlparse

register = template.Library()


class FreshMediaNotFound(BaseException):
    pass


def _fresh(filename, path):
    try:
        token = get_token(path)
    except OSError:
        if FAIL_IF_NON_EXIST:
            raise FreshMediaNotFound("File `%s` not found." % path)
        else:
            return ""
    else:
        url = urlparse.urljoin(settings.MEDIA_URL, "%s?%s" % (filename, token))
        return url


@register.simple_tag
def media(filename):
    path = os.path.join(settings.MEDIA_ROOT, filename)
    return _fresh(filename, path)

@register.simple_tag
def static(filename):
    path = os.path.join(settings.STATIC_ROOT, filename)
    return _fresh(filename, path)
