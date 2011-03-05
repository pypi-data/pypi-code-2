from django.db import models
import logging
from django.core.exceptions import MultipleObjectsReturned
from django.contrib import messages
from django.core.context_processors import request

from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User,Group
from django.contrib.sites.models import Site
from django.core.files.storage import FileSystemStorage

# Create your models here.
fs = FileSystemStorage(location='/usr/share/radioweb/static/media/audio')

def get_rel(song,tags):
    relatedtags = set()
    for tag in song.tags.all():
        if tag not in tags:
            relatedtags.add(tag)
    return list(relatedtags)

def render_float_length(floatvalue):
    ''' render_length
    takes a seconds float and renders a pretty string of the duration

    >>> render_float_length(12325426436.98235923875)
    '142655 days, 9:33:56'



    '''
    from datetime import timedelta


    human_length = timedelta(seconds=int(floatvalue))
    return str(human_length)


class Song(models.Model):
    '''
    Basic construction of the archive, the song is also a metadata set
    ``inside`` the file

    ``file`` the ogg file
    ``artist`` :model:`radio.Artist`
    '''

    file = models.FileField(upload_to='audio', 
                            help_text=_('this is the ogg file'))
    artist = models.ForeignKey('Artist',related_name=_('songs'))
    title = models.CharField(max_length=60)
    tags = models.ManyToManyField('Tag', related_name="songs", blank=True)
    genre = models.ForeignKey('Genre',related_name=_('songs'))
    album = models.ForeignKey('Album',related_name=_('songs'), blank=True, null=True)
    comments = models.TextField(max_length=400, 
                                blank=True,
                                help_text=_('this comments also get saved \
                                            on the file'))
    date = models.PositiveIntegerField( blank=True, null=True,
                            help_text=_('the year of release') )
    tracknumber = models.CharField(max_length=5, blank=True)
    channels = models.PositiveIntegerField( blank=True, editable=False, null=True)
    length = models.FloatField(blank=True, editable=False, null=True)
    license = models.CharField(blank=True, null=True,max_length=200)
    url = models.URLField(blank=True, null=True)
    bitrate =  models.PositiveIntegerField(blank=True, editable=False, null=True)
    samplerate =  models.PositiveIntegerField(blank=True, editable=False,null=True)
    filehash = models.CharField(max_length=32, editable=False,unique=True)
    plays = models.PositiveIntegerField(blank=True, editable=False, null=True,
                                        default=0)
    def add_tag(self,*args):
        '''
        add_tag
        model method for linking to an existing tag, or creating 
        one and then linking it:

        >>> onesong = Song.objects.all()[0]
        >>> onesong.add_tag('other')
        <super: <class 'Song'>, <Song object>>


        '''
        newtag, created = Tag.objects.get_or_create(tag=args[0].lower())
        self.tags.add(newtag)

        return super(Song, self) 

    def render_length(self):
        '''render_length
        gives a human readable version of the length of the song

        >>> onesong = Song.objects.all()[0]
        >>> onesong.render_length()
        '0:06:21'
        '''

        if not self.file:
            return 'No file'
        else:
            return  render_float_length(self.length)


    def save(self, *args, **kwargs):

        from liquidjango.utils import get_hash
        self.filehash = get_hash(str(self.file.path))

        logging.info(self.file.path)
        try:
            if self.id:
                if self.genre.genre not in [ s.tag for s in self.tags.all() ]:
                    self.add_tag(self.genre.genre)
        except  Genre.DoesNotExist:
            logging.info(self.genre.genre)

        return super(Song, self).save(*args, **kwargs)


    def related_tags(self):
	'''related tags
	performs some searches in the related objects and gives
	from those the tags this object doesn't have.
	>>> onesong = Song.objects.all()[0]
	>>> onesong.related_tags()
    [<Tag: krautrock-electronic>, <Tag: electronica & dance>]


	'''
        relatedtags = set()
        song_tags = self.tags.all()
        if self.album_id == None:
            for song in self.album.songs.all():
                songtags = get_rel(song,song_tags)
                for tag in songtags: 
                    relatedtags.add(tag)


        for song in self.artist.songs.all():
            songtags = get_rel(song,song_tags)
            for tag in songtags: 
                relatedtags.add(tag)

        for tag in self.artist.tags.all(): 
            if tag not in song_tags:
                relatedtags.add(tag)

        return list(relatedtags)

    class Meta:
        ordering = ["title"]
        verbose_name_plural = _('songs')

    @models.permalink
    def get_absolute_url(self):
        return ('liquidjango.views.onesong', [str(self.id)])
          
    def __unicode__(self):
        return u'%s' % (self.title)


class Album(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(upload_to='albumart', blank=True)
    tags = models.ManyToManyField('Tag', related_name="albums", blank=True)
    label = models.CharField(max_length=50, blank=True)
    release_date = models.PositiveIntegerField(max_length=4, null=True,
                verbose_name=_('the year of release for the album'))

    def get_playlists(self):
        '''
        >>> onealbum = Album.objects.all()[0]
        >>> onealbum.get_playlists()

        '''

        playlists = Playlist.objects.filter(entry__song__album=self).distinct()
        return playlists

    def get_genres(self):
        '''
        >>> onealbum = Album.objects.all()[0]
        >>> onealbum.get_genres()

        '''
        genres = Genre.objects.filter(songs__album=self).distinct()
        return genres

    def get_artists(self):
        '''
        >>> onealbum = Album.objects.all()[0]
        >>> onealbum.get_artists()

        '''
        artists = Artist.objects.filter(songs__album=self).distinct()
        return artists


    def __unicode__(self):
            return u'%s' % (self.title)

    def add_tag(self,word):
        '''
        >>> onealbum = Album.objects.all()[0]
        >>> onealbum.add_tag('love')
        >>> onealbum.save()

        '''
        newtag, created = Tag.objects.get_or_create(tag=word.lower())
        self.tags.add(newtag)
        return created


    class Meta:
        ordering = ["title"]
        verbose_name_plural = _('albums')

    def render_length(self):

        if not self.songs.count:
            return 'No songs'
        else:
            total = sum([x.length for x in self.songs.all()])
            return  render_float_length(total)


    @models.permalink
    def get_absolute_url(self):
        return ('liquidjango.views.onealbum', [str(self.id)])

    def related_tags(self):
        relatedtags = set()
        song_tags = self.tags.all()

        for song in self.songs.all():
            songtags = get_rel(song,song_tags)
            for tag in songtags: 
                relatedtags.add(tag)

        return list(relatedtags)


class Genre(models.Model):
    genre = models.CharField(max_length=50)
    def __unicode__(self):
            return u'%s' % (self.genre)
    class Meta:
        ordering = ["genre"]
        verbose_name_plural = _('genres')

    @models.permalink
    def get_absolute_url(self):
        tag = Tag.objects.get(tag=self.genre)
        return ('liquidjango.views.onetag', [str(tag.id)])


class Artist(models.Model):
    name = models.CharField(max_length=100,unique=True)
    comments = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag', 
                                  related_name="artists",
                                  blank=True)
    withmembersof = models.ManyToManyField('Artist',related_name="artists")

    def add_tag(self,*args):
        '''
        add_tag
        model method for linking to an existing tag, or creating 
        one and then linking it:
        >>> oneartist = Artist.objects.all()[0]
        >>> oneartist.add_tag('weird')

        '''
        for tag in args[0]:
            newtag, created = Tag.objects.get_or_create(tag=tag.lower())
            self.tags.add(newtag)

        return super(Artist, self) 


    def get_albums(self):
        '''
        get_albums

        >>> oneartist = Artist.objects.all()[0]
        >>> oneartist.get_albums()

        '''
        albums = Album.objects.filter(songs__artist=self).distinct()
        return albums


    @models.permalink
    def get_absolute_url(self):
        return ('liquidjango.views.oneartist', [str(self.id)])

    def related_tags(self):
        relatedtags = set()
        artist_tags = self.tags.all()


        for otherartist in self.withmembersof.all():
            for song in otherartist.songs.all():
                songtags = get_rel(song,artist_tags)
                for tag in songtags: 
                    relatedtags.add(tag)
            
        for song in self.songs.all():
            songtags = get_rel(song,artist_tags)
            for tag in songtags: 
                relatedtags.add(tag)
            
        logging.info(relatedtags)
        return list(relatedtags)

    def __unicode__(self):
        return u'%s' % (self.name)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = _('artists')

    def get_genres(self):
        genres = Genre.objects.filter(songs__artist=self).distinct()
        return genres


    def render_length(self):

        if not self.songs.count:
            return 'No songs'
        else:
            total = sum([x.length for x in self.songs.all()])
            return  render_float_length(total)

    def get_playlists(self):
        playlists = Playlist.objects.filter(entry__song__artist=self).distinct()
        return playlists 


class Playlist(models.Model):
    '''
    This playlists can be saved and submitted to the radio
    '''


    title = models.CharField(max_length=100,default=_('New Playlist'))
    owner = models.ForeignKey(User, editable=False, related_name="playlists")
    tags = models.ManyToManyField('Tag', related_name="playlists", blank=True)
    plays = models.PositiveIntegerField(blank=True, editable=False,default=0)
    randomize = models.BooleanField(blank=True,default=False,
                        help_text=_('shuffle every time we send it to the radio'))
    songs = models.ManyToManyField(Song,through='Entry', blank=True,
                                  null=True, related_name="playlists")

    def make_distinct(self):
        songs = self.songs.all().distinct()
        entries = self.entry_set.all()
        if songs.count() < entries.count():
            for song in songs:
                try:
                    self.entry_set.get(song=song)
                    pass
                except MultipleObjectsReturned:
                    self.entry_set.filter(song=song)[0].delete()    #deletes the
                                                                    #first occurrence of the song
            #self.make_distinct()
            return entries.count() -  songs.count()
        else:
            return

    def render_length(self):

        if not self.entry_set.count:
            return 'No songs'
        else:
            total = sum([x.song.length for x in self.entry_set.all()])
            return  render_float_length(total)


    def shuffle(self):
        entries = self.entry_set.all().order_by('?')
        for index,entry  in enumerate(entries):
            entry.position = index
            entry.save()

        return


    def arrange_positions(self):
        for index,entry  in enumerate(self.entry_set.all()):
            entry.position = index
            entry.save()
        return




    def related_tags(self):
        relatedtags = set()
        song_tags = self.tags.all()

        for song in self.songs.all():
            '''
            for word in song.title.split(" "):
                if len(word) > 4:
                    relatedtags.add(word)
                    '''
            asongtags = get_rel(song,song_tags)
            for tag in asongtags: 
                relatedtags.add(tag)


        return list(relatedtags)


    class Meta:
        verbose_name_plural = _('playlists')
        ordering = ['title']



    @models.permalink
    def get_absolute_url(self):
        return ('liquidjango.views.oneplaylist', [str(self.id)])
          
    def __unicode__(self):
        return _(u'%s') % self.title

    def save(self, *args, **kwargs):
        model = self.__class__
        self.arrange_positions()

        return super(Playlist, self).save(*args, **kwargs)


class Entry(models.Model):
    playlist = models.ForeignKey(Playlist,editable=False,verbose_name=_('playlist'))
    position = models.PositiveIntegerField()
    song = models.ForeignKey(Song,verbose_name=_('song'))



    def make_last(self):
        position = self.playlist.entry_set.all().reverse()[0].position
        self.position = position+1

    class Meta:
        verbose_name_plural = _('entries')
        ordering = ['position', 'song']

    def __unicode__(self):
       return u'%d - %s' % (self.position,self.song.title)

    def save(self, *args, **kwargs):
        model = self.__class__
        if self.position is None:
            try:
                last = model.objects.order_by('-position')[0]
                self.position = last.position + 1
            except IndexError:
                self.position = 0

        return super(Entry, self).save(*args, **kwargs)


class Tag(models.Model):
    tag = models.CharField(max_length=100,unique=True)
    def __unicode__(self):
        return u'%s' % (self.tag)

    @models.permalink
    def get_absolute_url(self):
        return ('liquidjango.views.onetag', [str(self.id)])

    class Meta:
        ordering = ["tag"]


if __name__ == "__main__":
    '''to enable doctests'''
    import doctest
    doctest.testmod()

