from django.contrib import admin
from birdland.models import Entry

class EntryAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'publish', 'status',)
    list_filter = ('status', 'author',)
    prepopulated_fields = {'slug': ('title',)}

    def formfield_for_dbfield(self, db_field, **kwargs):
        request = kwargs.get('request')
        field = super(EntryAdmin, self).formfield_for_dbfield(db_field, **kwargs)
        if request and db_field.name == 'author':
            field.initial = request.user.id
        return field

admin.site.register(Entry, EntryAdmin)
