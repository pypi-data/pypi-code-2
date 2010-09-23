from __future__ import absolute_import

from django.conf.urls.defaults import patterns, url

from .views import emailform_detail

urlpatterns = patterns(
    "",
    url(r'^(?P<slug>[-a-z0-9_]+)/embed/$',
        emailform_detail,
        {'embed' : True},
        name="emailform_detail"),

    url(r'^(?P<slug>[-a-z0-9_]+)/$',
        emailform_detail,
        name="emailform_detail"),
    )
