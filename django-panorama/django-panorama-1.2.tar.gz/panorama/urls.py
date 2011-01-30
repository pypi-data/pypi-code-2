"URL patterns for panorama"

from django.conf.urls.defaults import patterns, url
from django.views.generic import ListView, DetailView
from panorama.models import Panorama

urlpatterns = patterns('panorama.views',
  # Add url patterns here
  url(r'^$', ListView.as_view(model=Panorama), name='panorama_list'),
  url(r'^(?P<pk>\d+)$', DetailView.as_view(model=Panorama),
                        name='panorama_detail'),
  (r'^(?P<pk>\d+).json$', 'panorama_json'),
  (r'^note/(?P<pk>\d+)$', 'show_note'),
)
