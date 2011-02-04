import random
import sys
import mx.DateTime
import datetime
import time
from dm.ioc import *
from dm.dom.stateful import *
from dm.messagedigest import md5
from dm.dictionarywords import WEBKIT_NAME
from dm.dictionarywords import DJANGO_SECRET_KEY
from dm.exceptions import WebkitError
import string
import random

class Session(SimpleDatedObject):
    "Visitor session."

    registerKeyName = 'key'
    isUnique        = False
    key             = String(default='', isRequired=False)
    person          = HasA('Person', default=None)
    lastVisited     = DateTime(default=mx.DateTime.now, isRequired=False)

    def initialise(self, register):
        super(Session, self).initialise(register)
        if not self.key:
            self.key = self.createKey()
            while self.key in register: 
                # Shouldn't happen very often. :-)
                self.key = self.createKey()
            self.isChanged = True

    def createKey(self):
        "Returns new session key."
        randomPart = ''
        characterList = string.letters + string.digits
        for i in range(60):
            randomPart += random.choice(characterList)
        secretPart = self.dictionary[DJANGO_SECRET_KEY] 
        sessionKey = md5(randomPart + secretPart).hexdigest()
        return sessionKey

    def updateLastVisited(self):
        nowTime = mx.DateTime.now()
        try:
            if (int(nowTime) > int(self.lastVisited) + 10):
                self.lastVisited = nowTime
                self.save()
        except Exception, inst:
            self.log.error("Couldn't save lastVisited time: %s" % inst)

