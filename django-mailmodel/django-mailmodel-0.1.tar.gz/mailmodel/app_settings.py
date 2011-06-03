from django.conf import settings

MAILMODEL_CONFIG = {
    "INCLUDE_CAPTCHA" : False,
    "EMAIL_TITLE": u"Check out this",
    "APPS": [],
    "PUBLIC_CAPTCHA_KEY": "6LeFxwgAAAAAAGsK3bu4Ks4RAh2hcxGatYKL9nQv",
    "PRIVATE_CAPTCHA_KEY": "6LeFxwgAAAAAAJk18_gJOJtX6Tr90i6kKH6O6WnY"
}

MY_CUSTOM_SETTING = getattr(settings, 'MAILMODEL_CONFIG', {})
MAILMODEL_CONFIG.update(MY_CUSTOM_SETTING)

