from django.db.models import Q
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

MODELS = getattr(settings, 'YAMA_MODELS', {
    # Enter the models you wish to link to here,
    # in the form of key-value pairs as follows:
    # ('app_label', 'model_name') : Q(<filter>)
    # e.g.
    # ('auth', 'User') : Q(is_active=True),
})

VIEWS = getattr(settings, 'YAMA_VIEWS', (
    # List the views you wish to link to here, in
    # pairs of the form (<reverse-able name>, <display name>)
    # e.g.
    # ('blog.views.index', _('Blog index'))
    # or if you're using named url patterns:
    # ('blog-index', _('Blog index')),
))

