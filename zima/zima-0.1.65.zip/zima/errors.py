# -*- coding: utf-8 -*-
# Ошибки имиджборды.

import pprint

class ValuedError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return pprint.pformat(self.value)
    def __unicode__(self):
        return pprint.pformat(self.value)

# Ошибки хранилища
class StorageError(ValuedError):
    pass

class StorageCollisionError(ValuedError):
    pass

class Message404Error(ValuedError):
    pass

class File404Error(ValuedError):
    pass

    
# Ошибки капчи
class InvalidCaptchaError(ValuedError):
    pass

class Captcha404Error(ValuedError):
    pass

class CaptchaExpiredError(ValuedError):
    pass

# Ошибки вложений
class AttachDuplicationError(ValuedError):
	pass
    
class ForbiddenAttachTypeError(ValuedError):
    pass

class InvalidAttachError(ValuedError):
    pass
