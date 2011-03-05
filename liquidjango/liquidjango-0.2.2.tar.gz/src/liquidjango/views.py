'''
Views
'''

from django.shortcuts import render_to_response, get_object_or_404, \
get_list_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from radioweb.radio.forms import *
from radioweb.radio.models import *
from django.contrib.auth.models import User, Group
from django.contrib import messages
from mutagen.oggvorbis import OggVorbisHeaderError
from  radioweb.radio.utils import *
from django.db.models import F

from radioweb.radio import index 





def get_total_time(songqueryset):
    from datetime import timedelta

    totalmusictime = sum([x.length for x in songqueryset])
    d = timedelta(seconds=int(totalmusictime))
    return str(d)



def home(request):
    '''
    the homepage gives stats and action buttons for visitors

    ``last_tags``
    '''
    allsongs = Song.objects.all()
    allartists = Artist.objects.all()
    alltags = Tag.objects.all()
    allplaylists = Playlist.objects.all()
    allalbums = Album.objects.all()

    last_songs = allsongs.order_by('id').reverse()[:10]
    last_artists = allartists.order_by('id').reverse()[:10]
    last_tags = alltags.order_by('?')[:10]
    last_albums = allalbums.order_by('?')[:10]
    last_playlists = allplaylists.order_by('?')[:10]
    search_form = SearchForm()
    totalmusictime = get_total_time(allsongs)

    data= { _('songs'): allsongs.count(),
           _('artists'):allartists.count(),
           _('tags'): alltags.count(),
           _('albums'): allalbums.count(),
           _('total music time'): totalmusictime,
           _('playlists'): allplaylists.count(),
           _('djs'): User.objects.count(),
          }
    
    return render_to_response('home.html', {
                    'search_form': search_form, 
					'last_songs': last_songs,
					'last_artists': last_artists,
					'last_tags': last_tags,
					'last_playlists': last_playlists,
					'last_albums': last_albums,
					'data': data,
					'onair': onair(),
			},context_instance=RequestContext(request))
def list_playlists():
    '''
    gets the available playlists in the server
    '''
    lists = []
    for i in command_to_radio('list').split("\n"):
        if 'playlist' in i:
            lists.append(i.split(" ")[0])
    return lists

def get_requests(alive):
    '''
    to trim a request queue from the alive songs
    
    >>> alive = alive()
    >>> queue = get_requests(alive)
    >>> queue

    '''
    queue = []
    for i in alive:
        if '2nd_queue_pos' in i.keys():
            queue.append(i)
    return queue

def nextaudios(source):
    '''
    Given a source, gets the list of audios
    and looks for a record in the database 
    '''

    next = command_to_radio('%s.next' % source )
    return next.split("\n")






def requests(request):
    '''
    To analize the playlist in the liquidsoap

    Functions:
        * alive() from radio.utils:
            takes the rids of the songs currently on liquidsoaps memory
        * get_requests(alive) from here

    >>> now =  alive()
    >>> list = get_requests(now)
    >>> availableplaylists = list_playlists()
    '''
    search_form = SearchForm()
    now =  alive()
                  


    queue = get_requests(now) 
    playlists = {}
    for playlist in list_playlists():
        playlists[playlist] = nextaudios(playlist)



    return render_to_response('requests.html', {
                    'search_form': search_form, 
		    'onair': onair(),
                    'alive': now,
                    'playlists': playlists,
                    'queue': queue
			},context_instance=RequestContext(request))


def oneartist(request,object_id):
    '''
    A particular artist page

    All the info related to the artist. Soon will also have related artists and
    tags, or other thngs that help to create a :model:`radio.Playlist`


    **template**
    :template:`one_artist.html`

    '''
    artist = get_object_or_404(Artist, pk=object_id)

    if request.method == 'POST':
        tagform = TagForm(request.POST)
        tags = [ request.POST['tag'].split(",") ]
        for tag in tags:

            artist.add_tag(tag)
            messages.success(request,u'%(tag)s has been added to %(artist)s' % \
                         { 'tag': tag[0], 'artist':
                          artist.name})
        artist.save()

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/artist/'+str(artist.id))


    tagform = TagForm()
    search_form = SearchForm()
    playlists = []
    if request.user.is_staff:
        playlists = request.user.playlists


    bulkeditform = AllSongsinAlbumForm()
    return render_to_response('one_artist.html', {'user': request.user, 
					'artist': artist,
                    'search_form': search_form, 
					'tagform': tagform,
                    'next': '/artist/'+str(artist.id),
					'bulkeditform': bulkeditform,
                    'next': '/audio/artist/'+str(artist.id),
                    'playlists': playlists,
					'onair': onair(),
			},context_instance=RequestContext(request))

def onetag(request,object_id):
    tag =  get_object_or_404(Tag, pk=object_id)
    search_form = SearchForm()

    return render_to_response('one_tag.html', {'user': request.user, 
					'tag': tag,
                    'search_form': search_form, 
					'onair': onair(),
			},context_instance=RequestContext(request))

def onesong(request,object_id):
    thissong =  get_object_or_404(Song, pk=object_id)
    search_form = SearchForm()
    similar = Song.objects.filter(length=thissong.length).exclude(pk=thissong.id)
    if request.method == 'POST':
        tagform = AddTagForm(request.POST)
        if tagform.is_valid():

            tags =  tagform.data['tag'].split(",") 
            for tag in tags:
                newtag, created= Tag.objects.get_or_create(tag=tag.lower())
                thissong.tags.add(newtag)
                if created:
                    messages.success(request,_('%s was created') % newtag.tag)
                thissong.tags.add(newtag)
                #thissong.indexer.update()
                messages.success(request,_(u'%(tag)s was added to %(song)s') % \
                         { 'tag': newtag.tag,
                      'song': thissong.title})
                thissong.save()

                if 'NEXT' in request.POST:
                    return HttpResponseRedirect(request.POST['NEXT'])
                else:
                    return HttpResponseRedirect('/audio/'+str(thissong.id))
        else:
            messages.error(request,tagform.errors)
            if 'NEXT' in request.POST:
                return HttpResponseRedirect(request.POST['NEXT'])
            else:
                return HttpResponseRedirect('/audio/'+str(thissong.id))

    tagform = TagForm()
    playlists = []
    if request.user.is_staff:
        playlists = request.user.playlists

    return render_to_response('una.html', {'user': request.user, 
					'thissong': thissong,
                    'search_form': search_form, 
					'onair': onair(),
					'tagform': tagform,
					'similar': similar,
                    'playlists': playlists
			},context_instance=RequestContext(request))


def editseveralsongs(request):

    if request.method == 'POST':
                
                
        bulkeditform = AllSongsinAlbumForm(request.POST)
        changes = bulkeditform.changed_data

        for song_id in request.POST['songlist'].split(","):

            try:
                song = Song.objects.get(pk=song_id)
                messages.info(request,  'changing %s' % song )
                for change in changes:
                    if change in [ 'artist', 'genre','album']:
                        song.__setattr__(change+'_id', request.POST[change])
                        messages.info(request,  'changing %s' % change )
                    else:

                        song.__setattr__(change, request.POST[change])
                        messages.info(request,  'changing %s' % change )
            except:
                pass

            song.save()

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/')
    
    return render_to_response('playlist.html', {'user': request.user, 
                    'search_form': SearchForm(), 
                    'playlist_form': PlaylistForm(prefix='pls'),
					'onair': onair(),
					'bulkeditform': bulkeditform,
			},context_instance=RequestContext(request))




@login_required
def add_to_pls(request):
    '''
    Adds to a playlist, and creates one if needed
    '''


    if request.method == 'POST':
                
        playlist = ""
        if (request.POST['playlist'] == 'new'):
            playlist = Playlist(owner=request.user, title='New title')
            playlist.save()
            messages.info(request,_('a new playlist has been created'))
            position = 1
                
        else:
            playlist=Playlist.objects.get(pk=request.POST['playlist'])
            if playlist.entry_set.count():
                position = playlist.entry_set.all().order_by('position').reverse()[0].position+1
            else:
                position = 0
                
        for song_id in request.POST['songlist'].split(","):

            try:
                song=Song.objects.get(pk=song_id)
                newentry = Entry(playlist=playlist,song=song,position=position)
                newentry.save()
                messages.info(request,_(u'%s has been added to the playlist' % \
                                            song.title))
                position +=1

            except:
                pass

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/pls/'+str(playlist.id))
    
    return render_to_response('playlist.html', {'user': request.user, 
                    'search_form': SearchForm(), 
                    'playlist_form': PlaylistForm(prefix='pls'),
					'onair': onair(),
			},context_instance=RequestContext(request))

def onealbum(request,object_id):
    '''
    one_album


    '''
    
    thisalbum = get_object_or_404(Album, pk=object_id)
    if request.method == 'POST':
        tagform = TagForm(request.POST)

        if 'tag' in request.POST:
            thisalbum.add_tag(request.POST['tag'])
            thisalbum.save()
            messages.info(request,_(u'%s was added to album') % request.POST['tag'])
                

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/audio/album/'+str(thisalbum.id))
 

    #bulkeditform = AllSongsinAlbumForm(artistq=thisalbum.get_artists(),genreq=thisalbum.get_genres())
    bulkeditform = AllSongsinAlbumForm()
    #bulkeditform = AllSongsinAlbumForm(artistquery=Artist.objects.filter(songs__album=thisalbum).distinct())

    return render_to_response('album.html', {'user': request.user, 
                    'search_form': SearchForm(), 
					'onair': onair(),
                    'next': '/audio/album/'+str(thisalbum.id),
					'tagform': TagForm(),
					'bulkeditform': bulkeditform,
                    'album': thisalbum,
			},context_instance=RequestContext(request))




def oneplaylist(request,object_id):

    playobj = get_object_or_404(Playlist, pk=object_id)

    if request.method == 'POST':
        playlist_form = PlaylistForm(request.POST,instance=playobj)
        tagform = TagForm(request.POST,instance=playobj)
        last_form = MakeLastForm(request.POST)
        commandform = CommandtoRadioForm(request.POST)

        if commandform.is_valid():
            command = request.POST['command']
            if command == 'distinct':
                playobj.make_distinct()
            if command == 'shuffle':
                playobj.shuffle()


        if playlist_form.is_valid():
            playlist_form.save()

            if 'NEXT' in request.POST:
                return HttpResponseRedirect(request.POST['NEXT'])
            else:
                return HttpResponseRedirect('/pls/'+str(playobj.id))

        if tagform.is_valid():
            tag, created = Tag.objects.get_or_create(tag=request.POST['tag'])
            messages.info(request,_(u'tag %s added to playlist' % tag.tag ))
            if created:
                messages.info(request,_(u'tag %s created' % tag.tag ))

            playobj.tags.add(tag)
            playobj.save()

            if 'NEXT' in request.POST:
                return HttpResponseRedirect(request.POST['NEXT'])
            else:
                return HttpResponseRedirect('/pls/'+str(playobj.id))
        if last_form.is_valid():

            entry = Entry.objects.get(pk=tagform.data['entry'])            
            entry.make_last()
            entry.save()
            messages.info(request,_(u'entry %s sent to end of playlist') % \
                                    entry.song.title )

            if 'NEXT' in request.POST:
                return HttpResponseRedirect(request.POST['NEXT'])
            else:
                return HttpResponseRedirect('/pls/'+str(playobj.id))
 



    playlist_form = PlaylistForm(instance=playobj)

    last_form = MakeLastForm()
    
    bulkeditform = AllSongsinAlbumForm()
    return render_to_response('playlist.html', {'user': request.user, 
                    'search_form': SearchForm(), 
					'onair': onair(),
					'tagform': TagForm(),
					'playlist': playobj,
					'webhosturl': request.get_host(),
					'bulkeditform': bulkeditform,
                    'commandform' : CommandtoRadioForm(),
                    'playlist_form': playlist_form,
			},context_instance=RequestContext(request))

@login_required
def admin(request):
    user = request.user
    info = {}
    info['sources'] = command_to_radio('list').split("\n")
    info['stream_status'] = command_to_radio(settings.LIQ_SRC+'.status')
    info['playlists'] = {}
    allartists = Artist.objects.all()
    allsongs = Song.objects.all()
    allalbums = Album.objects.all()
    allplaylists = Playlist.objects.all()
 
    info['emptyartists'] = allartists.filter(songs=None)
    info['emptyalbums'] = allalbums.filter(songs=None)
    info['emptyplaylists'] = allplaylists.filter(songs=None)
    info['emptytags'] = Tag.objects.filter(songs=None,artists=None)
    info['hostname'] = request.get_host()

    queue = get_requests(alive()) 
    for playlist in list_playlists():
        info['playlists'][playlist] = nextaudios(playlist)


    if request.method == 'POST':
        command_form = CommandtoRadioForm(request.POST)
        if command_form.is_valid():
            if request.user.is_staff:
                if 'extra' in request.POST:
                    response = command_to_radio(str(request.POST['extra']+str(request.POST['command'])))
                else:

                    response = command_to_radio(str(request.POST['command']))
                messages.success(request,_(u'command results:  %s') % \
                             response.decode('ascii','ignore') )

        reload_form = ReloadForm(request.POST)
        if reload_form.is_valid():
            response = command_to_radio(str(request.POST['playlist'])+'.reload')
            messages.success(request,_(u'command results:  %s') % \
                             response.decode('ascii','ignore') )

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/requests')


    command_form = CommandtoRadioForm()
    reload_form = ReloadForm()
    return render_to_response('radioadmin.html', {'user': request.user, 
                    'search_form': SearchForm(), 
					'onair': onair(),
                    'user': user,
                    'queue': queue,
                    'info': info,
                    'command_form': command_form,
                    'reload_form': reload_form,
					'tagform': TagForm(),
			},context_instance=RequestContext(request))


@login_required
def deleteentry(request,entry_id):
    if request.method == 'POST':
        entry = Entry.objects.get(pk=entry_id)
        entry.delete()
        messages.info(request,_(u'song %s deleted from playlist' % \
                      entry.song.title))

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/')











def playlist_2_radio(request,object_id):
    playobj = get_object_or_404(Playlist, pk=object_id)

    if request.method == 'POST':
        #command = str('music.uri http://yp.cryptodrunks.net'+playobj.get_absolute_url()+'/pls/send\n')
        if playobj.randomize == True:
            songs = playobj.songs.all().order_by('?')
        else:
            songs = [ x.song for x in playobj.entry_set.all() ]
        for song in songs:
            play(song)
            messages.info(request, _(u'song %s sent to radio' % song ))
        #response = command_to_radio(command)
        #command = str('music.reload\n')
        #messages.info(request, response )
        #response = command_to_radio(command)


        return redirect(playobj)





def pls_file(request,object_id):
    '''
    pls_file(request,playlist_id)

    Generates a .pls file for the server to stream the
    playlist to the user.

    '''
    
    playobj = get_object_or_404(Playlist, pk=object_id)
    if playobj.randomize == True:
        urls =  [ (song.file.url) for song in playobj.songs.all().order_by('?')]
        entries = playobj.songs.all().order_by('?')
    else:
        urls =  [ (entry.song.file.url) for entry in playobj.entry_set.all() ]
 
    response = HttpResponse("\n".join(urls), mimetype='audio/x-scpls')
    return response


def pls_radio(request,object_id):
    '''
    pls_file(request,playlist_id)

    Generates a .pls file to send to the radio.

    '''
    
    playobj = get_object_or_404(Playlist, pk=object_id)

    if playobj.randomize == True:
        urls =  [ (song.file.path) for song in playobj.songs.all().order_by('?') ]
    else:

        urls =  [ (entry.song.file.path) for entry in playobj.entry_set.all() ]
    response = HttpResponse("\n".join(urls), mimetype='audio/x-scpls')
    return response




def editsong(request,object_id):
    '''
    edit a song in the database:

    a view that allows to edit a song as a database record,
    and then add the new tags to the ogg file and
    updates the database record of the md5 hasfile, 
    used for indexing and deduplicating of the audio
    
    
    >>> song =  get_object_or_404(Song, pk=4)
    >>> song.file.url  != ''
    True

    >>> song.title = 'new title'
    >>> song.save()
    >>> tag , created = Tag.objects.get_or_create(tag='places')
    >>> tag.artists.all()
    []
    >>> assert tag
    >>> song.tags.add(tag)
    >>> song.save()
    
    newtags = change_tags(song,editform.cleaned_data,editform.changed_data)


    '''
    song =  get_object_or_404(Song, pk=object_id)
    search_form = SearchForm()
    editform = SongEditForm(instance=song)
    if request.method == 'POST':
        ''' if there is data submitted from a form,
        we will try to edit the song
        
        >>> editform = SongEditForm(request.POST)
        '''
        editform = SongEditForm(request.POST,instance=song)
        if editform.is_valid():

            editform.save()


            return HttpResponseRedirect('/audio/'+str(song.id))

        else:
            editform = SongForm(request.POST)

    return render_to_response('una.html', {'user': request.user, 
					'thissong': song,
					'onair': onair(),
                    'search_form': search_form, 
					'editform': editform,
			},context_instance=RequestContext(request))

def playonradio(request,object_id):
    '''Plays a song right after the current playing song'''

    if request.method == 'POST':

        song =  get_object_or_404(Song, pk=object_id)

        song.plays = F('plays') + 1
        song.save()

        play(song) #function on radio.utils.py
        messages.success(request, _('song submitted to the radio playlist. \
                     it will be played soon'))

        if 'NEXT' in request.POST:
            return HttpResponseRedirect(request.POST['NEXT'])
        else:
            return HttpResponseRedirect('/requests')


@login_required
def skipcurrent(request):
    '''
    Skipcurrent


    This view makes the liquidsoap client to forward to the next song in the
    playlist.
    Please use sparely! the crossfade doesn't work on it...

    '''
    command = str(settings.LIQ_SRC+'.skip\n')
    command_to_radio(command)
    messages.success(request,_(' song has been skipped'))

    return HttpResponseRedirect('/')


def import_file(request):
    '''
    A view that unifies all importing options

    Importing options enforce terrible validation 
    for the archive to have some consistency.
    Provided that the archive(:model:`radio.Song`) will be 
    streamed always in the same quality and format, 
    and that real time reencoding is a process we want 
    to spare our server of, we enforce the audio codec, 
    bitrate, samplerate.

    A file has to have this conditions to be accepted on the radio database:
        * Ogg/vorbis format
        * 2 channels minimum
        * 64000 bitrate
        * 44100 samplerate
        * Artist, Title, Genre tags

    This files will be added to the collection of the site

        * submitting a file through a webform
        * submitting a link to a file
        * inserting a path already on the system

    **Context**

        * ``RequestContext``
        * ImportURLForm
        * UploadFileForm
        * ImportFromArchive




    **Template:**

    :template:`import.html`


    '''
    search_form = SearchForm()
    
    if request.method == 'POST':
        newsong = import_audio_from_archive(request.POST['path'].encode("utf-8","ignore"))
        if type(newsong) == Song:
            messages.success(request,_('song imported! thanks!'))
            return HttpResponseRedirect('/audio/%d' % newsong.id)
        else:
            messages.error(request,newsong)
            return HttpResponseRedirect('/')
    else:
        user = request.user
        c = { 'onair': onair(), 
             'user': user ,
             'import_url_form': ImportURLForm(),
             'file_upload_form' : UploadFileForm(),
                    'search_form': search_form, 
             'archive_path_form' : ImportFromArchive()
            }


        return render_to_response('import.html', c,context_instance=RequestContext(request))



def dropbox(request):
    '''
    A view for the members of the community to 
    add their own files

    
    from a file that is already on the server:

    >>> path = '/usr/share/radio/music/nerd/Supernerd.ogg'
    >>> newsong = import_audio_from_archive(path)#doctest: +IGNORE_EXCEPTION_DETAIL


    '''

    user = request.user
    search_form = SearchForm()
    last_songs = Song.objects.all().order_by('id').reverse()[:15]
    simpleform = UploadFileForm()
    if request.method == 'POST':
        simpleform = UploadFileForm(request.POST, request.FILES)
        if simpleform.is_valid():

            temp = handle_uploaded_file(request.FILES['file'])
            newsong = songfromlocalfile(temp)
            if type(newsong) == Song:

                messages.success(request, _('song %s imported, thanks!') % newsong)
                os.remove(temp)
                return HttpResponseRedirect('/audio/%d/' % newsong.id)

            else:
                messages.error(request, newsong)

                os.remove(temp)


    return render_to_response('submit.html', {'user': user, 
					'last_songs': last_songs,
                    'search_form': search_form, 
					'onair': onair(),
					'upload_form': simpleform,
        			},context_instance=RequestContext(request))

def search(request):
    results = []
    if request.GET:
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
            model = MODEL_MAP.get(search_form.cleaned_data['model'])
            if not model:
                index.indexer = index.complete_indexer
            else:
                index.indexer = model.indexer

            try:
                results = index.indexer.search(query).prefetch()
            except:
                results = []


    else:
        search_form = SearchForm()

    playlists = []
    if request.user.is_staff:
        playlists = request.user.playlists

    return render_to_response('search.html', {
        'results': results, 
        'onair': onair(),
        'search_form': search_form,
        'playlists': playlists,
        #'playlists': EntryFormSet(playlist__owner__id=request.user.id),
    },context_instance=RequestContext(request))


@login_required
def sanify(request):

    allartists = Artist.objects.all()
    allsongs = Song.objects.all()
    allalbums = Album.objects.all()
    alltags = Tag.objects.all()
    emptyartists = allartists.filter(songs=None,name__in=[" ","",None])
    emptyalbums = allalbums.filter(songs=None)
    emptytags = alltags.filter(songs=None,artists=None)


    if request.method == 'POST':
        command_form = CommandtoRadioForm(request.POST)
        if command_form.is_valid():
            messages.info(request,_(u'form is valid? %s') % command_form.is_valid())
            messages.info(request,command_form.data['command'])
            if command_form.data['command'] == 'clean':
                messages.info(request,_(u'cleaning unrelated records...'))
                files = clean_files_with_no_record()
                messages.info(request,_(u'cleaning unrelated files: %s') % \
                                        files )
                try:
                    clean_object(Artist)
                    clean_object(Tag)
                    clean_object(Album)
                    clean_object(Playlist)
                except:
                    pass


            if 'NEXT' in request.POST:
                return HttpResponseRedirect(request.POST['NEXT'])
            else:
                return HttpResponseRedirect('/sanify')

       




    command_form = CommandtoRadioForm()
    search_form = SearchForm()

    data= { 
        _('songs'): allsongs.count(),
        _('artists'):allartists.count(),
        _('tags'): Tag.objects.count(),
        _('albums'): allalbums.count(),
        _('playlists'): Playlist.objects.count(),
    }

    return render_to_response('admin.html', {
        'onair': onair(),
        'data': data,
        'emptyartists': emptyartists,
        'emptyalbums': emptyalbums,
        'emptytags': emptytags,
        'command_form': command_form,
        'search_form': SearchForm(),
    },context_instance=RequestContext(request))
    

if __name__ == "__main__":
    '''to enable doctests'''
    import doctest
    doctest.testmod()

