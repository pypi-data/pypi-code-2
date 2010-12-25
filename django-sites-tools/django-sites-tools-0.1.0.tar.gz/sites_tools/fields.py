from django.db import models
from django.contrib.sites.models import Site

class SiteField(models.OneToOneField):
    """
    A 
    
    """
    def __init__(self, **kwargs):
        super(SiteField, self).__init__('sites.Site', **kwargs)

class MultipleSitesField(models.ManyToManyField):

    def __init__(self, **kwargs):
        super(MultipleSitesField, self).__init__('sites.Site', **kwargs)

try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^sites_tools\.fields"])
except ImportError:
    pass
