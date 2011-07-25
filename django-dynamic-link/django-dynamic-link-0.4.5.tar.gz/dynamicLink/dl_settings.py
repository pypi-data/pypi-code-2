
#!/usr/bin/python
# -*- coding:utf-8 -*-
# This Python file uses the following encoding: utf-8

import settings
from django.utils.translation import ugettext_lazy as _

# A folder from witch walk down so you can choose a file
MEDIA = settings.MEDIA_ROOT

# Specify your serve path: /www.example.com/serve/link/3839hd8HKl3/example.zip
DOWNLINK_SERVE_PATH = 'serve'

# It stands here for not violate the DRY priciple.
TEXT_REQUEST_DOES_NOT_EXIST = _(u'This request is faulty')
TEXT_REQUEST_IS_EXPIRED = _(u'Sorry, this request is already expired')
