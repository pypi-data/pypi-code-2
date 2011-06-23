import mimetypes
from django.conf import settings


for ext, type in getattr(settings, "MIMETYPES", {}).items():
    mimetypes.add_type(type, ext)
