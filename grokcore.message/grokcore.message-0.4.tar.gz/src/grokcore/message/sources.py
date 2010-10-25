# -*- coding: utf-8 -*-

import grokcore.component as grok
from grokcore.message import IMessageSource, PersistentMessage


class UniqueMessageSource(grok.GlobalUtility):
    """A source that handles a unique message.
    """
    grok.baseclass()
    grok.implements(IMessageSource)

    message = None

    def send(self, message, type=u'message'):
        self.message = PersistentMessage(message, type)

    def list(self, type=None):
        if self.message is None:
            return
        if type is None or self.message.type == type:
            yield self.message

    def delete(self, message):
        if message is self.message:
            self.message = None
        else:
            raise KeyError(message)
