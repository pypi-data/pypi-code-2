from django import template
from django.conf import settings
from django.template import Context, Template
from django.template.loader import get_template

register = template.Library()

try:
    FORM_TEMPLATE = settings.BLUETRAIN_DEFAULT_FORM
except NameError:
    FORM_TEMPLATE = 'pages/default_form.html'

@register.filter
def as_default_form(form):
    template = get_template()
    c = Context({'form':form})
    return template.render(c)