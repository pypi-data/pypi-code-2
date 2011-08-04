from django.contrib import admin

from models import Chunk


class ChunkAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name', ], }

admin.site.register(Chunk, ChunkAdmin)
