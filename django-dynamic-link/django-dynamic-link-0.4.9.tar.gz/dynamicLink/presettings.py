#!/usr/bin/python
# -*- coding:utf-8 -*-
# This Python file uses the following encoding: utf-8

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

# A path to a directory from witch walk down so you can choose your files.
DYNAMIC_LINK_MEDIA = settings.MEDIA_ROOT

# A string that modify the serve url path:
# /www.example.com/DYNAMIC_LINK_URL_BASE_COMPONENT/link/3839hd8HKl3/example.zip
DYNAMIC_LINK_URL_BASE_COMPONENT = 'serve'

# It's here because of not violate the DRY priciple.
TEXT_REQUEST_DOES_NOT_EXIST = _(u'This request is faulty')
TEXT_REQUEST_IS_EXPIRED = _(u'Sorry, this request is already expired')

# Look for data that overwrite the defaults
# - variables from dl_settigns.py overwrite thus from settings and form presettings
# - variables from settings.py overwrite thus form presettings
# As you see it can't be used both at once. Settings.py is only used if there
# is no dl_settings.py
try:
    from dl_settings import *
except ImportError:
    try:
        from settings import DYNAMIC_LINK_URL_BASE_COMPONENT
    except ImportError:
        pass
    try:
        from settings import DYNAMIC_LINK_MEDIA
    except ImportError:
        pass