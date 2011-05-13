from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('desktopnotifications.views',
    url(r'^$', 'index'),
    url(r'^get/(\d+)/?$', 'get_notification'),
    url(r'^get_tags/?$', 'get_tags'),
    url(r'^is_authenticated/?$', 'check_is_authenticated'),
) + patterns('',
    url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login_notification.html'}),
)