#!/usr/bin/env python
#-*- coding: utf-8 -*-

from django.conf import settings
from django.utils import simplejson
from django.http import HttpRequest
import base64
import types
import time
import httpagentparser

class MixpanelError(Exception):pass
class MixpanelWarning(UserWarning):pass

class DummyBackend(object):

    def __init__(self, *args, **kwargs):

        self.base_properties = {}
        token = getattr(settings, 'MP_API_TOKEN', None)

        if not token:
            raise ValueError, 'Mixpanel API token not defined'
        self.base_properties['token'] = token
        
        # for other backend, you must has a connection instance
        self.connect = None

    def _build_mp_request_url(self, data):
        parma = base64.b64encode(simplejson.dumps(data))
        mp_request_url = "http://api.mixpanel.com/track/?data=" + parma
        return mp_request_url

    def fetch_event(self):
        raise NotImplementedError, '%s not implemented this method' % self.__class__.__name__
    
    def send_event(self, url):
        '''
        do send event, must overwrite this
        '''
        if not self.connect:
            pass

    def build_request_data(self, request):
        '''
        only get request ip address
        if you want to add more properties from request, you should overwrite this method
        @param request:
        '''
        if request.META.has_key('HTTP_X_REAL_IP'):
            ip = request.META['HTTP_X_REAL_IP']
        elif request.META.has_key('REMOTE_ADDR'):
            ip = request.META['REMOTE_ADDR']
        else:
            ip = '127.0.0.1'

        user_agent = request.META['HTTP_USER_AGENT']
        return {'ip': ip, 'user-agent':' '.join(httpagentparser.simple_detect(user_agent))}

    def trackMixpanelEvent(self, event_name, properties={}, request=None):
        '''
        do not overwrite this, unless you know what's you want.
        @param event_name:
        @param properties:
        @param request:
        '''
        #check input paramas
        if type(event_name) is not types.StringType:
            raise MixpanelError, 'event name must be a string'        
        if type(properties) is not types.DictType:
            raise MixpanelError, 'properties must be a dict'
        print isinstance(request, HttpRequest)
        if not isinstance(request, HttpRequest) and request != None:
            raise MixpanelError, 'request must is HttpRequest class instance or None value'

        # build rest data
        data = {}
        data['event'] = event_name
        properties = properties

        properties.update(self.base_properties)
        # append GMT time
        properties['time'] = int(time.mktime(time.gmtime(time.time())))
        
        if request:
            properties.update(self.build_request_data(request))

        data['properties'] = properties
        
        if settings.DEBUG:
            print data
            
        # send event
        self.send_event(self._build_mp_request_url(data))

    def trackfunnelMixpanelEvent(self, funnel, step, goal, properties={}, request=None):
        '''
        do not overwrite this, unless you know what's you want.
        @param funnel:
        @param step:
        @param goal:
        @param properties:
        @param request:
        '''
        #check input paramas 
        if type(funnel) is not types.StringType:
            raise MixpanelError, 'funnel must be a string'
        if type(step) is not types.IntType:
            raise MixpanelError, 'step must be a int number'
        if type(goal) is not types.StringType:
            raise MixpanelError, 'goal must be a string'            
        if type(properties) is not types.DictType:
            raise MixpanelError, 'properties must be a dict'
        if not isinstance(request, HttpRequest) and request != None:
            raise MixpanelError, 'request must is HttpRequest class instance or None value'
        
        # build data
        data = {}
        data['event'] = 'mp_funnel'
        
        properties = properties
        properties.update(self.base_properties)
        # append GMT time
        properties['time'] = int(time.mktime(time.gmtime(time.time())))
        properties['funnel'] = funnel
        properties['step'] = step
        properties['goal'] = goal
        
        if request:
            properties.update(self.build_request_data(request))
            
        data['properties'] = properties  
        
        if settings.DEBUG:
            print data        

        # send event
        self.send_event(self._build_mp_request_url(data))        
        
MixpanelBackend = DummyBackend




