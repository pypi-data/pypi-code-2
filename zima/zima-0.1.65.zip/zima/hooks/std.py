# -*- coding: utf-8 -*-

from bottle import request

# Проверка на размер сообщения и попытку перезаписать те поля
# документа, которые перезаписывать не надо.

#------------------------------------------------------------------
# Исключения

class TooFatTextError(Exception):
    pass

class ForbiddenField(Exception):
    def __init__(self, val = 'Unknown field'):
        self.value = val
    def __str__(self):
        return repr(self.value)

#------------------------------------------------------------------
# Конструктор перехватчиков
def maker(cfg, hook):

    def chk_field(kv):
        if kv[0] not in cfg.allowedFields:
            raise ForbiddenField(kv[0])
        return kv

    def store_id(doc):
        doc['poster'] = request.environ['REMOTE_ADDR']
        return doc

    def chk_doc(doc):
        if 'message' in doc and len(doc['message']) > cfg.messageMaxSize:
            raise TooFatTextError()
        return doc

    return [('customField', chk_field),
            ('newMessage', chk_doc),
            ('newMessage', store_id)]


