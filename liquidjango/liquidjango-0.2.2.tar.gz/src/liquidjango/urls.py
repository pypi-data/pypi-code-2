from django.conf.urls.defaults import *
from django.contrib import admin
from liquidjango.models import *
from django.contrib.auth.views import login , password_reset , logout_then_login

# Uncomment the next two lines to enable the admin:

urlpatterns = patterns('django.contrib.auth.views',
    (r'^login$', 'login'),
    (r'^logout$', 'logout_then_login'),
                       )     

urlpatterns += patterns('radioweb.radio.views',
    (r'^drop', 'dropbox'),
    (r'^skipcurrent', 'skipcurrent'),
    (r'^audio/(?P<object_id>\d+)/edit$', 'editsong'),
    (r'^audio/edit$', 'editseveralsongs'),
    (r'^audio/(?P<object_id>\d+)/play$', 'playonradio'),
    (r'^audio/(?P<object_id>\d+)$', 'onesong'),
    (r'^audio/album/(?P<object_id>\d+)$', 'onealbum'),
    (r'^audio/import$', 'import_file'),
    (r'^audio/sanify$', 'sanify'),
    (r'^radioadmin$', 'admin'),
    (r'^artist/(?P<object_id>\d+)$', 'oneartist'),
    (r'^pls/add$', 'add_to_pls'),
    (r'^pls/(?P<object_id>\d+)$', 'oneplaylist'),
    (r'^pls/entry/(?P<entry_id>\d+)/delete$', 'deleteentry'),
    (r'^pls/(?P<object_id>\d+)/send$', 'playlist_2_radio'),
    (r'^pls/(?P<object_id>\d+)/pls/send$', 'pls_radio'),
    (r'^pls/(?P<object_id>\d+)/pls$', 'pls_file'),
    (r'^tag/(?P<object_id>\d+)$', 'onetag'),
    (r'^search$', 'search'),
    (r'^requests$', 'requests'),
    (r'^', 'home'),

)

