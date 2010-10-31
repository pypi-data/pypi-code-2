#coding: utf-8
from django.conf.urls.defaults import *

urlpatterns = patterns('merchant_api.views',
   url('^callback$', 'merchant_callback', name='merchant_callback'),
)

