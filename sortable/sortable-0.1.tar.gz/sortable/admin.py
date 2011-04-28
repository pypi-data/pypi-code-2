from django.contrib import admin

class SortableAdmin(admin.ModelAdmin):
    # Make instances reorderable
    list_editable = ('position',)
    list_display = ('position', )
    class Media: js = ('js/admin_list_reorder.js',)


