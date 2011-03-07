from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from dbresolver import autodiscover_views, get_dbresolver_patterns
from player.block import autodiscover_blocks

admin.autodiscover()
autodiscover_views()
autodiscover_blocks()

urlpatterns = patterns('',
    url(r'^$', 'website.views.home', name='home'),
    url(r'^news/', include('news.urls')),
    url(r'^manage/', include('player.manage.urls')),
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += get_dbresolver_patterns()
