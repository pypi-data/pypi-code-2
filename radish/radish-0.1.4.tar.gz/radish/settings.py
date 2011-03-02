from django.conf import settings

ADMIN_LOGIN    = getattr(settings,'RADISH_ADMIN_LOGIN','admin')
ADMIN_PASSWORD = getattr(settings,'RADISH_ADMIN_PASSWORD','admin')

DEBUG = getattr(settings,'RADISH_DEBUG',False)
