from django.contrib import admin
from captcha.models import Captcha


class CaptchaAdmin(admin.ModelAdmin):
    pass

admin.site.register(Captcha, CaptchaAdmin)
