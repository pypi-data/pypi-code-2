# -*- coding: utf-8
from django.contrib import admin

from green_comments.models import Comment

class CommentAdmin(admin.ModelAdmin):
    list_display = ['created', 'user']

admin.site.register(Comment, CommentAdmin)
