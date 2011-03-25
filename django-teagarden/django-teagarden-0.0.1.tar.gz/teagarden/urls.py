# -*- coding: utf-8 -*-

import os

from django.conf.urls.defaults import *
from django.contrib import admin


HERE = os.path.abspath(os.path.dirname(__file__))
ANCHOR = os.path.join(HERE, './')
STATIC = os.path.join(ANCHOR, '..', 'static/')


admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/set_project/$', 'teagarden.admin_views.set_project'),
    (r'^admin/', include(admin.site.urls)),
    (r'^signin/$', 'django.contrib.auth.views.login'),
    (r'^signout/$', 'django.contrib.auth.views.logout'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {
        'document_root': STATIC}),
)

js_info_dict = {
    'packages': ('teagarden',),
}

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns += patterns(
    'teagarden.views',
    #('', include('helpers.urls')),
    (r'^$', 'index'),
    (r'^(\d+)/create_table_comment$', 'create_table_comment'),
    (r'^table/(\d+)/comment/(\d+)/discard$', 'discard_table_comment'),
    (r'^table/(\d+)/comment/(\d+)/publish$', 'publish_table_comment'),
    (r'^dashboard$', 'dashboard'),
    (r'^project/(\d+)$', 'project'),
    (r'^projects$', 'projects'),
    (r'^settings$', 'edit_settings'),
    (r'^(\d+)/star_field$', 'star_field'),
    (r'^(\d+)/star_table$', 'star_table'),
    (r'^starred$', 'starred_objects'),
    (r'^table/(\d+)$', 'table'),
    (r'^(\d+)/unstar_field$', 'unstar_field'),
    (r'^(\d+)/unstar_table$', 'unstar_table'),
    (r'^user/(.+)$', 'show_user'),
    (r'^user_popup/(.+)$', 'user_popup'),
    )
