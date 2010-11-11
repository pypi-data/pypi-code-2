from django.contrib.contenttypes.models import ContentType

from genericforeignkey.forms import GenericAdminModelForm


class GenericAdmin(object):

    form = GenericAdminModelForm


def register(site):
    from genericforeignkey.admin_register import GenericContentTypeAdmin
    site.register(ContentType, GenericContentTypeAdmin)
