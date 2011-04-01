# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'django_cachepurge.tests.testingmodels',
    (r'^content/(?P<pk>\d+)/edit$', 'edit_url_model'),
    )
