# -*- encoding: utf-8 -*-
from django.conf import settings

FRONTWEB_SITE_NAME = getattr(settings, "FRONTWEB_SITE_NAME", u"Front web")
FRONTWEB_URL = getattr(settings, "FRONTWEB_URL",  "http://127.0.0.1:8000")
FRONTWEB_DATA = getattr(settings, "FRONTWEB_DATA", u"data")
FRONTWEB_DESCRIPCION = getattr(settings, "FRONTWEB_DESCRIPCION", u"Un sitio de notas")
FRONTWEB_AUTHOR = getattr(settings, "FRONTWEB_AUTHOR", u"Hugo Ruscitti")
