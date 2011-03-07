import string, random,os, logging
from urllib2 import urlopen
from django.utils.translation import ugettext_lazy as _
from django.core.validators import ValidationError
from mutagen import oggvorbis
from django.core.files.temp import NamedTemporaryFile
from django.core.files import File
from hashlib import md5
import telnetlib, time, datetime, threading
from django.conf import settings
from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from liquidjango.models import Song, Artist, Album, Genre
from django.core.context_processors import request
from django.shortcuts import get_object_or_404
import os

#######################
# Telnet interface    #
#######################

def command_to_radio(command):
    '''command_to_radio
    
    sends a command to the telnet interface,
    and returns the result

    >>> command_to_radio('jingles.reload')
    'OK\n'

    '''

    try:
        tn = telnetlib.Telnet(settings.LIQ_HOST,port=settings.LIQ_PORT)
        tn.write(str(command)+'\n')
        response = tn.read_until("END")
        tn.close()
    except:
        response = ''

    return response[0:-3]

def onair():

    rid = command_to_radio('on_air')

    if rid != '\n':
        metadata = get_meta(rid)
    else:

        from xml.dom import minidom
        import urllib
        radiodata = urllib.urlopen('http://abbadingo.net:8000/adalovelace.ogg.xspf')
        xmldoc = minidom.parseString("".join(radiodata.readlines()))

	try:
	        artistname = xmldoc.getElementsByTagName('creator')[1].childNodes[0].data
        	songname = xmldoc.getElementsByTagName('title')[1].childNodes[0].data
	except IndexError:
	        artistname = 'Unknown'
        	songname = 'Unkown'

        metadata = {}
        metadata['artist'] = artistname
        metadata['title'] = songname
    try:
        # bug here: problems with encoding of the filename, django doesnt find
        # the songs with weird chars in title/artist

        song = Song.objects.filter(title__iexact=songname,
                                   artist__name__iexact=artistname)

        metadata['id'] = song[0].id
    except:
        pass


    return metadata




def get_meta(rid):
    '''
    gets metadata with a rid number
    '''
    metadata_string = command_to_radio('metadata '+rid)
    metadata = {}
    for line in metadata_string.splitlines():
        values = line.split('=')
        if len(values) >1:
            if values[0] != 'END':
                metadata[values[0]] = values[1].strip('"')
    try:
        # bug here: problems with encoding of the filename, django doesnt find
        # the songs with weird chars in title/artist

        song = Song.objects.filter(title__iexact=unicode(metadata['title'],
                                                    'utf-8').strip(' '),
                                   artist__name__iexact=unicode(metadata['artist'],
                                                        'utf-8').strip(' '))

        metadata['id'] = song[0].id
    except:
        pass


    return metadata

def alive():
    '''
    Gets the songs in memory of the liquidsoap
    '''
    alives = command_to_radio('alive')
    songs = []
    for rid in alives.split(" "):
        songs.append(get_meta(rid))
    return songs

def play(song):
    '''
    this function pushes a :model:``liquidjango.models.Song``g in the request playlist 
    of the liquidsoap

    >>> song =  get_object_or_404(Song, pk=1)
    >>> play(song)

    '''
    command = '%s.push %s' % ( settings.LIQ_QUEUE, song.file.path)
    logging.info(u'command: %s' % command)
    return command_to_radio(command)






#######################
# file importing      #
#######################

def get_hash(path):
    '''
    To verify the file is new
    '''
    m = md5()
    f = file(path, 'rb') # open in binary mode
    while True:
        t = f.read(1024)
        if len(t) == 0: break # end of file
        m.update(t)
    return m.hexdigest()

def import_audio_from_archive(path):
    '''to import a file from a url, and make a song object with it'''
    
    newsong = songfromlocalfile(path)

    return newsong

def import_songs_from_folder(path,recursive=False):
    '''
    import all ogg files in a folder

    >>> path = '/usr/share/radio/music/obreros/'
    >>> errors = import_songs_from_folder(path)
    UnicodeError
    >>> len(errors)
    35


    '''
    errorlist = {}
    
    for newfile in os.listdir(path):
        if newfile[-4:] == '.ogg':
            try:

                newsong = songfromlocalfile(str(path+newfile))

                if type(newsong) == Song:
                    pass
                else:
                    if newsong == u'this file is already on the database':
                        pass
                    else:
                        errorlist[path+newfile] = newsong
            except:
                pass

        else:
            if (recursive != True):
                pass
            else:
                if os.path.isdir(path+newfile):
                    try:
                        logging.info(u': Importing files on dir %s' % path+newfile)
                        import_songs_from_folder(path+newfile+'/', recursive=True)
                    except:
                        pass
                        #logging.info(': Could not import %s' % path+newfile)
    

    return errorlist




def songfromlocalfile(tempfile):
    '''we add a file from the local machine
    
    >>> temp = os.path.join(os.getcwd(), '/fixtures/Krow-Moe_Remix-A_Glorious_Dawn.ogg')
    >>> songfromlocalfile(temp)
    '''


    tempsong = SimpleUploadedFile('test.ogg',open(tempfile,'rb').read(),content_type='application/ogg')
    filedata = { 'file': tempsong }


    data = {}
    validation = FileForm(data, filedata) #using the form validation



    if validation.is_valid():
        initial, tags = import_tags(tempfile)

        song = Song(**initial)
        newfilename = [tags['artist'].encode("ascii","ignore"),
                       '-', initial['title'].encode("ascii","ignore"),
                       '.ogg']
        song.file.save("".join(newfilename), filedata['file'], save=False)
        #we check if artist exists, and if not, we create it.
        artist,created =     Artist.objects.get_or_create(name=tags['artist'])

        song.artist = artist
        #same with genre and later with tag and album
        genre, created = Genre.objects.get_or_create(genre = tags['genre'])
        song.genre = genre
        song.save()


       	texttags = tags['genre'].split(",")
        
        for onetag in texttags:
            song.add_tag(onetag)        
            logging.info(u'%s' % onetag)

        if 'album' in tags.keys():
            '''album is optional, so we check if it's there before'''
            #assert False, tags['album']
            album, created = Album.objects.get_or_create(title=tags['album'])
            song.album = album
            song.album.save()
        try: 
            song.save()
            return song
        except:
       
            os.remove("".join(newfilename))
            return validation.errors.values()[0][0] 
    else:
        #logging.info(u'%s:\n %s' % \
        #             ( tempfile, validation.errors.values()[0][0]))
        return validation.errors.values()[0][0]

        

def clean_files_with_no_record():
    '''
    Removes files


    cleans files that are not linked to a db record
    (better to try to import from this folder first!)

    >>> clean_files_with_no_record()

    '''
    path = settings.AUDIO_DIR
    reals = []
    for song in Song.objects.all():
            reals.append(song.file.path)

    for audio in os.listdir(path):
        if (path+audio) not in reals:
            logging.info(u'cleaning file %s' % audio)
            os.remove(path+audio)



def clean_object(object):
    emptyobjects = object.objects.filter(songs=None)
    for i in emptyobjects:
        i.delete()
        logging.info(u'deleted %s' % i)
        return (_(u'deleted %(len)d %(obj)s with no songs') % \
                { 'len': len(emptyobjects),
                'obj':object} 
               )

def validate_newfile(audio):
    '''Validates the content before it gets saved to the database,
    post-processing as less as possible.'''
    if not audio.content_type in ['audio/vorbis',
                                  'application/ogg',
                                  'application/octet-stream',
                                  'audio/ogg',
                                  'application/x-ogg']:
        raise ValidationError(_('this file is not ogg, is %s' % audio.content_type))

    tempfile = handle_uploaded_file(audio)
    #filehash = md5(file(tempfile).read()).hexdigest()
    filehash = get_hash(tempfile)

    new = Song.objects.filter(filehash=filehash)
    if new.exists():
        os.remove(tempfile)
        raise  ValidationError(_("this file is already on the database"))

    #assert False,tempfile
    tags, taglist = import_tags(tempfile)
    if 'artist' not in  taglist:
        os.remove(tempfile)
        raise  ValidationError(_("artist tag missing"))
    if 'genre' not in  taglist:
        os.remove(tempfile)
        raise  ValidationError(_("genre tag missing"))
    if not tags:
        os.remove(tempfile)
        raise  ValidationError(_("not an ogg file"))
    if tags['bitrate'] < 64000:
        os.remove(tempfile)
        raise  ValidationError(_("file less than 64000 bitrate"))
    if tags['samplerate'] != 44100:
        os.remove(tempfile)
        raise  ValidationError(_("file has a samplerate different of 44100"))

#    if tags['channels'] < 2:
#        os.remove(tempfile)
#        raise  ValidationError(_("mono file"))
    
    os.remove(tempfile)




def handle_uploaded_file(f):
    
    filename = '/tmp/'+"".join(random.sample(string.letters+string.digits,8))+'.ogg'
    destination = open(filename, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    return filename


from mutagen import oggvorbis
def import_tags(temppath):
    '''
    import the ogg tags to use for the new song object

    #provided a tempfile
    >>> temppath = os.path.join(os.getcwd(), '/fixtures/mono_file.ogg')

    #we get its vorbis tags
    >>> tags = oggvorbis.Open(temppath)
    >>> tags.info.bitrate
    80000

    >>> test = import_tags(temppath)
    >>> print test


    '''
    tags = oggvorbis.Open(temppath)
    initial = {'bitrate': tags.info.bitrate,
               'samplerate':tags.info.sample_rate,
               'length':tags.info.length,
               'channels':tags.info.channels,
               'filehash': get_hash(temppath)}
    taglist = {}
    for tag, value in tags.tags:

        #logging.info(u'working with tag %s' % tag )
        if tag.lower()  in ['title','comments','date','tracknumber']:
            try:
                initial[tag.lower()] = value
            except:
                
                logging.info(u'could not add %s' % value )

        elif tag.lower() == 'date':
            #logging.info(u'date tag added %s' % tag )

            taglist[tag.lower()] = value[0:4]
        else:
            #logging.info(u'normal tag added: %s' % tag )

            taglist[tag.lower()] = value

    return initial, taglist

def change_tags(song,tags,changes):
    '''
    This snippet is for changing the file tags
    of a song if its db record changes, as well as 
    updating the resulting hashfile in the db

    
    '''

    dafile = oggvorbis.Open(song.file.path)
    for tag in changes:
        if tag == 'genre':
            dafile[tag] = tags['genre'].genre
            song.tag = tags['genre']
        else:
            try:
                dafile[tag] = str(tags[tag])
                song.tag = tags[tag]

            except:
                raise
    try:
        dafile.save()
        song.filehash = get_hash(song.file.path)
        
        song.save()

    except: 
        raise
    return file

class FileForm(forms.Form):
    '''to validate the new file'''
    file = forms.FileField(validators=[validate_newfile])


def updatefile(song):
    '''
    This snippet is for changing the file tags
    of a song if its db record changes, as well as 
    updating the resulting hashfile in the db


    
    '''

    dafile = oggvorbis.Open(song.file.path)
    taglist = ['filehash','length','title','license','comments',
               'date']

    for tag in taglist:
        try:
            dafile[tag] = str(song.__getattribute__(tag))
        except:
            raise
    try:
        dafile['genre'] = song.genre.genre
        dafile['album'] = song.album.title
        dafile['artist'] = song.artist.name
    except:
        pass

            
    try:
        dafile.save()
        
    except ValueError:
        pass
    return True




if __name__ == "__main__":
    '''to enable doctests'''
    import doctest
    doctest.testmod()


