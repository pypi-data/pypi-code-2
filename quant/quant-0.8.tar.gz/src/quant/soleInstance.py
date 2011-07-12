import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'quant.django.settings.main'

import quant.application

application = quant.application.Application()

