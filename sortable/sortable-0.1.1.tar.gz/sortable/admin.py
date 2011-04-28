from django.contrib import admin

class SortableAdmin(admin.ModelAdmin):
    # Make instances reorderable
    list_editable = ('position',)
    list_display = ('position', )
    class Media: js = (
        'http://ajax.googleapis.com/ajax/libs/jquery/1.5/jquery.min.js',
        'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js',
        'js/django-admin-sortable.js',)
