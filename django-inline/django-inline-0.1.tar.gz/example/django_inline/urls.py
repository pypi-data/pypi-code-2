from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('django_inline.views',
    url(r'^widget/', 'widget', name='django_inline_widget'),
    url(r'^update/', 'update', name='django_inline_update'),
)
