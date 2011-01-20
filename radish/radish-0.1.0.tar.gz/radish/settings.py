from django.conf import settings

ADMIN_LOGIN    = getattr(settings,'RADISH_ADMIN_LOGIN','admin')
ADMIN_PASSWORD = getattr(settings,'RADISH_ADMIN_PASSWORD','admin')

BROWSER = getattr(settings,'RADISH_BROWSER','firefox')

