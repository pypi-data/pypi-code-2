#!/usr/bin/env python

from hashlib import md5
from urllib import urlencode

class UGravatar(object):
    __url__ = "http://www.gravatar.com/avatar/"
    email = None
    size = 40

    def __init__(self,**kwargs):
        for k in kwargs:
            self.__setattr__(k,kwargs[k])
        return None
    
    def __repr__(self):
        return "UGravatar('%s')" % self.email

    def __str__(self):
        if not self.email:
            return False

        return '%s%s?%s' % (self.__url__,md5(self.email).hexdigest(),urlencode({'s':self.size}))

