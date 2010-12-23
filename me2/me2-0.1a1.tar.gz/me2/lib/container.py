# me2/container.py
#
#

""" container for bot to bot communication. """

__version__ = "1"

## me2 imports

from me2.lib.gozerevent import GozerEvent
from me2.contrib.simplejson import dumps

## xmpp import

from me2.contrib.xmlstream import NodeBuilder, XMLescape, XMLunescape

## basic imports

import hmac
import uuid
import time
import hashlib

## defines

idattributes = ['createtime', 'origin', 'type', 'idtime', 'payload']

## functions

def getid(container):
    name = ""
    for attr in idattributes:
        try: name += str(container[attr])
        except KeyError: pass
    return uuid.uuid3(uuid.NAMESPACE_URL, name).hex

## classes

class Container(GozerEvent):

    """ Container for bot to bot communication. Provides a hmac id that can be checked. """

    def __init__(self, origin=None, payload=None, type="event", key=None):
        GozerEvent.__init__(self)
        self.createtime = time.time()
        self.origin = origin
        self.type = str(type) 
        self.payload = payload
        self.makeid()
        if key: self.makehmac(key)
        else: self.makehmac(self.id)

    def makeid(self):
        self.idtime = time.time()
        self.id = getid(self)

    def makehmac(self, key):
        self.hash = "sha512"
        self.hashkey = key
        self.digest = hmac.new(key, self.payload, hashlib.sha512).hexdigest()
