from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('staging.views',
    url(r'^ajax/revision/$', 'staging_revision', name='staging_revision'),
    url(r'^ajax/start_push/$', 'start_push', name='start_push'),
    url(r'^ajax/make_push/$', 'make_push', name='make_push'),
    url(r'^ajax/finish_push/$', 'finish_push', name='finish_push'),
    url(r'^check_repository/$', 'check_repository', name='check_repository'),
    url(r'^download_repository/$', 'download_repository', name='download_repository'),
)
