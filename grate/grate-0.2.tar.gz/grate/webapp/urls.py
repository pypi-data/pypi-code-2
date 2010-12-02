from django.conf.urls.defaults import *
from django.conf import settings


urlpatterns = patterns('',
    url(r'^accounts/login/', 'django.contrib.auth.views.login',
        {'template_name': 'login.html'}, name='login'),
    url(r'^accounts/logout/', 'django.contrib.auth.views.logout',
        {'next_page': '/'}, name='logout'),

    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.ROOT('media')}, name='media'),

    (r'^', include('sewer.urls', namespace='sewer')),
)
