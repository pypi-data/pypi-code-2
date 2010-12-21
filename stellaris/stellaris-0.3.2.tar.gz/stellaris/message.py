# -*- coding: iso-8859-15 -*-
# (c) Mikael Högqvist

from stellaris.utils import id_generator

id_gen = id_generator()

class Message(object):

    def __init__(self, msgid=None):
        if msgid == None:
            self.msgid = id_gen.next()
        else:
            self.msgid = msgid

    def __repr__(self):
        return "<%s - %s>" % (self.__class__.__name__, ', '.join(["%s: %s" % (attr, getattr(self, attr)) for attr in dir(self) if not attr.startswith('__')]))

class MethodCallMsg(Message):
    def __init__(self, msgid, method, *args, **kwargs):
        self.method = method
        self.args = args
        self.kwargs = kwargs
        Message.__init__(self, msgid=msgid)
    
class MethodCallResultMsg(Message):
    def __init__(self, msgid):
        self.result = None
        self.fail = False
        Message.__init__(self, msgid=msgid)
