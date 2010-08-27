#encoding:utf-8
from django.conf import settings
from django.conf.urls.defaults import patterns, url, include
from helmholtz.access_control.admin import access_control_admin

urlpatterns = patterns('',
    (r'^admin/', include(access_control_admin.urls)),
    url(r'^login/$', 'helmholtz.access_control.views.login_session', {'template_name':'login.html'}, name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', {'login_url':settings.LOGIN_URL}, name='logout'),
    url(r'^download/file/(?P<file_id>\w*)/$', 'helmholtz.access_control.views.download_file', name='download-file'),
) 
