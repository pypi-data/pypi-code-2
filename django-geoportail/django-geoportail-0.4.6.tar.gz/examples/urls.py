from django.conf.urls.defaults import *


urlpatterns = patterns('examples.views',
    url(r'^$', 'home', name='home'),
    url(r'^form/$', 'form', name='form'),
)
