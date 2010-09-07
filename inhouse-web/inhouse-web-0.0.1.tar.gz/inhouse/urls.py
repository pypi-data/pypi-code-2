# -*- coding: utf-8 -*-

# TODO: Urls auf Hauptebene oder unter Inhouse?

import os

from django.conf.urls.defaults import *
from django.contrib import admin


HERE = os.path.abspath(os.path.dirname(__file__))
ANCHOR = os.path.join(HERE, './')
STATIC = os.path.join(ANCHOR, '..', 'static/')

admin.autodiscover()


urlpatterns = patterns(
    '',
    (r'^admin/inhouse/project/(\d+)/default_steps/$', 'inhouse.admin_views.default_steps'),
    (r'^admin/', include(admin.site.urls)),
    (r'^signin/$', 'django.contrib.auth.views.login'),
    (r'^signout/$', 'django.contrib.auth.views.logout'),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',  {
        'document_root': STATIC}),
)

js_info_dict = {
    'packages': ('inhouse',),
}

urlpatterns += patterns('',
    (r'^jsi18n/$', 'django.views.i18n.javascript_catalog', js_info_dict),
)

urlpatterns += patterns(
    'inhouse.views',
    (r'^$', 'index'),
    (r'^add_timer$', 'add_timer'),
    (r'^booking_popup/(.+)$', 'booking_popup'),
    (r'^(\d+)/clear_timer$', 'clear_timer'),
    (r'^company$', 'company'),
    (r'^company/phonelist$', 'phone_list'),
    (r'^dashboard$', 'dashboard'),
    (r'^dashboard/starred$', 'starred_bookings'),
    (r'^dashboard/timeline$', 'timeline'),
    (r'^(\d+)/pause_timer$', 'pause_timer'),
    (r'^overview$', 'overview'),
    (r'^profile$', 'edit_profile'),
    (r'^projects$', 'show_projects'),
    (r'^(\d+)/remove_timer$', 'remove_timer'),
    (r'^search', include('haystack.urls')),
    (r'^(\d+)/star_booking$', 'star_booking'),
    (r'^(\d+)/start_timer$', 'start_timer'),
    (r'^time$', 'time'),
    (r'^time/edit/(\d+)$', 'edit_booking'),
    (r'^time/history/(\d+)$', 'show_history'),
    (r'^time/undo$', 'undo_booking_change'),
    (r'^time/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/$', 'show_day'),
    (r'^time/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/new$', 'new_booking'),
    (r'^time/today$', 'show_today'),
    (r'^(\d+)/unstar_booking$', 'unstar_booking'),
    (r'^user/(\d+)$', 'show_user'),
    (r'^edit_timer$', 'edit_timer'),
    (r'^user_popup/(.+)$', 'user_popup'),
)

# Admin
urlpatterns += patterns(
    '',
    (r'^admin/bookstore/report/$', 'inhouse.admin_views.default_steps'),
)

# JSON
urlpatterns += patterns(
    'inhouse.json',
    (r'^json/get_customer_projects$', 'get_customer_projects'),
    (r'^json/get_project_graph/(\d+)$', 'get_project_graph'),
    (r'^json/get_project_steps$', 'get_project_steps'),
    (r'^json/get_project_tracker$', 'get_project_tracker'),
    (r'^json/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d+)/get_weekly_graph$', 'get_weekly_graph'),
    (r'^json/issue$', 'issue'),
)

# XML-RPC
urlpatterns += patterns(
    'inhouse.xmlrpc',
    (r'^xmlrpc$', 'handle_xmlrpc'),
)
