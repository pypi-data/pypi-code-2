from django import template
from django.conf import settings
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from htmlsanitizer.utils.constants import DEFAULT_SANITIZER


register = template.Library()

@register.filter(name='sanitize')
@stringfilter
def sanitize(value, sanitizer_name='__default__'):
    # get sanitizer
    if sanitizer_name == '__default__':
        sanitizer = DEFAULT_SANITIZER
    else:
        try:
            sanitizer = getattr(settings, sanitizer_name)
        except AttributeError:
            return "Sanitizer '%s' not found" % (sanitizer_name)
    # TODO : catch some common exceptions ... once we know what those are
    return mark_safe(sanitizer.clean(value))
sanitize.is_safe = True
