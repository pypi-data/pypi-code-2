'''
Indexer

The djapian indexer will help us to make some sense of all this songs...

'''
from djapian import space, Indexer, CompositeIndexer
from radioweb.radio.models import *


space.add_index(Genre, attach_as='indexer')
space.add_index(Tag, attach_as='indexer')


class SongIndexer(Indexer):
    fields = ['comments',('title',2), 'album', 'artist']
    tags = [
        ('title', 'title', 2),
        ('artist', 'artist'),
        ('genre', 'genre'),
        ('tags','tags', 2)
    ]

space.add_index(Song, SongIndexer, attach_as='indexer')

class ArtistIndexer(Indexer):
    fields = [ ('artist', 2), 'tags', 'withmembersof', 'songs' ]
    tags = [
        ('artist', 'name') ,
        ('tags', 'tags'),
        ('artist', 'withmembersof')
    ]


space.add_index(Artist, ArtistIndexer, attach_as='indexer')


complete_indexer = CompositeIndexer(Genre.indexer,
                                    Artist.indexer,
                                    Tag.indexer,
                                    Song.indexer)

