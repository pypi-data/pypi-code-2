#!/usr/bin/env python
#-*- coding: utf-8 -*-

from mixpanel_django.backends import dummy
import urllib2
import warnings

class DirectBackend(dummy.DummyBackend):
    
    def __init__(self, *args, **kwargs):
        super(DirectBackend, self).__init__(*args, **kwargs)
        handler = urllib2.HTTPHandler()
        self.connect = urllib2.build_opener(handler)
        self.connect.addheaders = [('User-agent', 'MixpanelDjango/0.1')]

    def send_event(self, url):
        '''
        overwrite me for other backends
        '''
        
        try:
            fp = self.connect.open(url)
        except:
            raise dummy.MixpanelError, 'send event error'
        res = fp.read()
        if res != '1':
            warnings.warn('event was not logged: %s' % url, dummy.MixpanelWarning)
        fp.close()

MixpanelBackend = DirectBackend