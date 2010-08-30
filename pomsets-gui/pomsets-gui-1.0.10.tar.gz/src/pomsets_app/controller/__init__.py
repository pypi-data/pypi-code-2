import copy
import functools
import logging
import os
import Queue
import threading
import threadpool
import urlparse


import pomsets.resource as ResourceModule

KEY_CONTROLLER_ACCESS_KEY = 'controllerAccessKey'
KEY_CONTROLLER_SECRET_KEY = 'controllerSecretKey'
KEY_CONTROLLER_SERVICE_NAME = 'controllerServiceName'

def parseUrl(url):
    
    result = urlparse.urlparse(url)
    host = result.hostname
    port = result.port
    path = result[2]
    isSecure = (result[0] == 'https')
    
    return {
        'isSecure':isSecure,
        'host':host,
        'port':port,
        'path':path
    }


def defaultEC2Values():

    controllerAccessKey = os.getenv('EC2_ACCESS_KEY')
    controllerSecretKey = os.getenv('EC2_SECRET_KEY')
    url = os.getenv('EC2_URL')

    values = parseUrl(url)
    values.update(
        {
            KEY_CONTROLLER_ACCESS_KEY:controllerAccessKey, 
            KEY_CONTROLLER_SECRET_KEY:controllerSecretKey,
            KEY_CONTROLLER_SERVICE_NAME:'eucalyptus'
        }
    )
    return values
    



class Thread(threading.Thread):

    def __init__(self, function):
        threading.Thread.__init__(self)
        self._function = function
        return
        
    def run(self):
        self._function()
        return
    
    # END class Thread
    pass

