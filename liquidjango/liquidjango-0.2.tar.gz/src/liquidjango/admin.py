from django.contrib import admin
from radioweb.radio.models import *

class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'length', 'filehash')

admin.site.register(Song, SongAdmin)

class ArtistAdmin(admin.ModelAdmin):
    pass
admin.site.register(Artist, ArtistAdmin)

class TagAdmin(admin.ModelAdmin):
    pass
admin.site.register(Tag, TagAdmin)

class PlaylistAdmin(admin.ModelAdmin):
    pass
admin.site.register(Playlist, PlaylistAdmin)

class EntryAdmin(admin.ModelAdmin):
    pass
admin.site.register(Entry, EntryAdmin)

class AlbumAdmin(admin.ModelAdmin):
    pass
admin.site.register(Album, AlbumAdmin)
