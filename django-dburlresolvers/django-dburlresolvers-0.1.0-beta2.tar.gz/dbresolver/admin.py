from django.contrib import admin

from dbresolver.forms import URLPatternForm
from dbresolver.models import URLPattern


class URLPatternAdmin(admin.ModelAdmin):
    form = URLPatternForm


admin.site.register(URLPattern, URLPatternAdmin)
