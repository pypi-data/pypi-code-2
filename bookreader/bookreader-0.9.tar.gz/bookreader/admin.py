from django.contrib import admin

from bookreader.models import Repository, Collection, Book, Page, Link, Annotation
from bookreader import harvesting



class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'repository', 'handle',)
    list_display_links = ('name',)
    list_filter = ('repository',)
    search_fields = ('name',)
    actions = ('load_books',)
    
    def load_books(self, request, queryset):
        for collection in queryset:
            results = harvesting.load_books(collection)
            self.message_user(request, '%d books loaded and %d books skipped '
                              'for %s' % (results[0], results[1], collection.name,)) 
    
    load_books.short_description = "Load books for selected collections"

class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'type', 'identifier', 'published',)
    list_display_links = ('title',)
    list_filter = ('collection', 'published', 'type', )
    search_fields = ['title', 'creator',]
    fieldsets = (
        (None, {'fields': ('type','thumbnail')}),
        ('References', {'classes': ('collapse',),
                        'fields': ('work','canonical')}))
    
    actions = ['update_metadata', 'create_pages', 'load_links', 'update_structure']
    
    def create_pages(self, request, queryset):
        for book in queryset:
            results = harvesting.BookHarvester(book).create_pages()
            self.message_user(request, '%d pages created for %s' % 
                              (results, book.title,))
    
    create_pages.short_description = "Load all pages for selected books"
    
    def load_links(self, request, queryset):
        for book in queryset:
            harvesting.BookHarvester(book).create_links()
            self.message_user(request, 'Links loaded for %s' % (book.title,))
    
    load_links.short_description = u'Load links for selected books'
    
    def update_metadata(self, request, queryset):
        for book in queryset:
            results = harvesting.BookHarvester(book).update_metadata()
            if results:
                self.message_user(request, 'Metadata reloaded for "%s"' % (book.title,))
    
    update_metadata.short_description = u'Update metadata for selected books'
    
    def update_structure(self, request, queryset):
        for book in queryset:
            results = harvesting.BookHarvester(book).update_structure()
            if results:
                self.message_user(request, 'Structure updated for %s' % (book.title,))
    
    update_structure.short_description = u'Update structure for selected books'

class PageAdmin(admin.ModelAdmin):
    list_display = ('book', 'title', 'sequence', 'internal',)
    list_display_links = ('title',)
    #list_editable = ('title', 'sequence', 'jp2_url')
    list_filter = ('book','internal',)
    search_fields = ['book', 'title']

class LinkAdmin(admin.ModelAdmin):
    list_display = ('book', 'title', 'mimetype','bundle',)
    list_display_links = ('title',)
    list_filter = ('book','mimetype','bundle',)
    search_fields = ('book','title','url','mimetype',)

class AnnotationAdmin(admin.ModelAdmin):
    list_display = ('book', 'offset','length','structural','text',)
    list_filter = ('book','structural',)
    search_fields = ('book','text',)

admin.site.register(Repository)
admin.site.register(Collection, CollectionAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Annotation, AnnotationAdmin)
