from django.contrib import admin
from django_mailchimp_forms.models import MailingList

class MailingListAdmin(admin.ModelAdmin):
    pass

admin.site.register(MailingList, MailingListAdmin)
