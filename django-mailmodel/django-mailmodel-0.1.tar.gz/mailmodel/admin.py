#-*- coding: utf-8- -*-
from django.contrib import admin
from models import MailModel

class MailModelForm(admin.ModelAdmin):
    list_display = ('name', 'email', 'recipient_name', 'recipient_email')
    
admin.site.register(MailModel, MailModelForm)
