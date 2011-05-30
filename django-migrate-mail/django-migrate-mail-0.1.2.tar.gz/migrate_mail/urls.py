# -*- encoding: utf-8 -*-

from django.conf.urls.defaults import *
from .views import index, migrate, migrate_process, migrate_results, migrate_delete
from .forms import MigrationForm
import os

# dirty hack to distribute static files along with app
# shouldn't  be an issue due to the nature of the app
STATIC_PATH = os.path.join(os.path.dirname(__file__), 'static')

urlpatterns = patterns('',
    url(r'^$', index, name="migrate_mail.index"),
    url(r'^migration/(?P<migration>\d+)/$', migrate, name="migrate_mail.migrate"),
    url(r'^migration/process/(?P<migration>\d+)/$', migrate_process, name="migrate_mail.migrate_process"),
    url(r'^migration/results/(?P<migration>\d+)/$', migrate_results, name="migrate_mail.migrate_results"),
    url(r'^migration/delete/(?P<migration>\d+)/$', migrate_delete, name="migrate_mail.migrate_delete"),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', kwargs={'document_root': STATIC_PATH}),
)
