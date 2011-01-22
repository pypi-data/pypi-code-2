#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('netcash.views',
    url(
          r'^data/(?P<secret>.+)/$',
          'data_handler',
          name='netcash_data'
    ),
    url(
          r'^accept/$',
          'result_handler',
          {'template_name': 'netcash/accept.html'},
          name='netcash_accept'
    ),
    url(
          r'^reject/$',
          'result_handler',
          {'template_name': 'netcash/reject.html'},
          name='netcash_reject'
    ),
)
