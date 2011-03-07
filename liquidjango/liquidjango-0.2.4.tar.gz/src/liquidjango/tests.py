"""
This file demonstrates two different styles of tests (one doctest and one
unittest). These will both pass when you run "manage.py test".

Replace these with more appropriate tests for your application.
"""

from django.test import TestCase
from django.test.client import Client
from django.http import Http404
import os

from liquidjango.models import *
from liquidjango.index import *
from liquidjango.views import *
from liquidjango.utils import *

CURPATH = os.path.dirname(os.path.abspath(__file__))

class SimpleTest(TestCase):
    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.failUnlessEqual(1 + 1, 2)

class LiquidsoapTest(TestCase):
    def setUp(self):
        import telnetlib
        from django.conf import settings
        self.c = Client()

    def test_connection(self):
        tn = telnetlib.Telnet(settings.LIQ_HOST,port=settings.LIQ_PORT)
        self.assertTrue(tn.host==settings.LIQ_HOST)
        logging.info(u'test telnet connection:  host: %s' % tn.host)
        tn.close()

    def test_commands_to_liquidsoap(self):
        commands_av = command_to_radio('list')
        logging.info(u'test telnet sources available: \n%s' % commands_av)
        self.assertTrue('jingles' in commands_av)
        self.assertTrue('source' in onair().keys())

    def test_push_and_ignore_song(self):
        song = Song.objects.all()[4]
        playme = play(song)
        nextsongs = alive()
        logging.info(u'test_push_and_ignore_song: %s' % str(nextsongs))
        self.assertTrue(song.file.path in str(nextsongs))
        takeout = command_to_radio('request.ignore %s\n' % playme)
        logging.info(u'test_push_and_ignore_song: %s' % takeout)
        nextsongs = alive()
        self.assertTrue("skip': 'true', 'title': '', 'filename':" in str(nextsongs))
        self.failUnlessEqual(takeout, 'OK\n')

# here i should call a method for check if the file 
# is in queue, but it's still not written....

class FileImportTest(TestCase):
    def setUp(self):
        self.path = '/usr/share/radio/music/nerd/Supernerd.ogg'

    def test_import_from_radio(self):
        self.newsong = import_audio_from_archive(self.path)
        self.assertTrue(self.newsong.title == 'Supernerd')

        logging.info(u'song created: %(song)s, with id %(id)d' % \
                     { 'song': self.newsong.title, 'id': self.newsong.id} )
        self.assertTrue(self.newsong.artist.name == 'Paolo e chiarO')

    def test_channel_validation(self):
        path = os.path.join(CURPATH, 'fixtures/mono_file.ogg')
        newsong = import_audio_from_archive(path)
        self.assertFalse(newsong == None)
        logging.info(u'test_channel_validation new song imported: %s' % newsong)

    def test_artist_tag(self):
        path = os.path.join(CURPATH, 'fixtures/artist_tag_missing.ogg')
        newsong = import_audio_from_archive(path)
        #logging.info(u'new song: %s' % newsong)
        self.assertTrue( 'artist tag missing' in newsong )

   
class WebTest(TestCase):

    from django.test import client

    def setUp(self):
        self.files = [os.path.join(CURPATH, 'fixtures/Amiri_Baraka-Dope.ogg'),
                      os.path.join(CURPATH, 'fixtures/mono_file.ogg'),
                      os.path.join(CURPATH, 'fixtures/genre_tag_missing.ogg')]
        self.c = Client()
        self.c.login(username='test',password='test')

    def test_login(self):

        response = self.c.get('/')

        self.assertTrue('you are logged in as test' in response.content)
        logging.info(u'login as test succeeded!')

       


    def test_submit_file(self):
        '''is the submit form working?'''

        f = open(self.files[0])
        response = self.c.post('/drop', { 'file': f, 
                                         'accept': True,
                                        }) 
        self.failUnlessEqual(response.status_code,302)
        response = self.c.get('/')
        self.failUnlessEqual(response.status_code,200)
        self.failUnless('<li class="success">song Dope imported, thanks!</li>' \
                        or 'this file is already on the database' in response.content)
        baraka = Song.objects.filter(title="Dope")[0]
        self.failUnlessEqual(baraka.artist.name,'Amiri Baraka')
        tag , created = Tag.objects.get_or_create(tag='black power')
        baraka.tags.add(tag)
        baraka.save()
        logging.info(u'added tag black power to %s' % baraka )

        f.close()

        othertag =  Tag.objects.get(tag='black power')
        logging.info(u'tag %s found!' % othertag)
        
        response = self.c.get('/tag/'+str(othertag.id))
        logging.info(u'tag %s found!' % othertag)
        
        self.failUnlessEqual(response.status_code,200)
        self.failUnless('Caspian Hat Dance' in response.content)
        self.failUnless('<b>Dope</b> by Amiri Baraka' in response.content)
        self.failUnless('<li>used in:' in response.content)


    def test_validation(self):

        f = open(self.files[2])
        drop = self.c.post('/drop', { 'file': f, 'accept': True , 'NEXT':
                               '/audio/4590'}) 
        f.close()
        #logging.info(drop.content)
        self.failUnlessEqual(drop.status_code,200)
        self.failUnless('<ul class="errorlist"><li>genre tag missing</li></ul>' \
                        in drop.content)
        


    def test_homepage(self):
        '''opening the homepage'''
        response = self.c.get('/')
        self.assertTrue('artists' in  response.content)
        self.failUnlessEqual(response.status_code, 200)


    def test_import_and_add_tag(self):

        logging.info('importing songs')
        folder = os.path.join(CURPATH, 'fixtures/')
        newsongs = import_songs_from_folder(folder)

        logging.info('new songs: ')
        logging.info(newsongs)
        self.assertTrue(len(newsongs)==2)
        #logging.info(newsongs)
        self.assertTrue('genre tag missing' in newsongs.values())
        self.assertTrue('artist tag missing' in newsongs.values())
        
        logging.info(Song.objects.all())
        song =Song.objects.filter(title='Dope')[0]

        self.failUnlessEqual(song.artist.name,'Amiri Baraka')
        logging.info(u'song found: %s' % song)

        response = self.c.get('/audio/'+str(song.id))
        #logging.info(response)
        self.assertTrue(response.status_code,200)
        self.assertTrue('artist' in  response.content)
        self.assertTrue('Amiri Baraka' in  response.content)





        response = self.c.post('/audio/'+str(song.id),{'tag':'people', 
                                'csrfmiddlewaretoken':'02b2f45d81d9b6e0ba3e1e0fc02aa9ba',
                                'song_id': str(song.id)

                                })
        logging.info(u'submitted tag people. response code: %s' % response.status_code)
        self.failUnlessEqual(response.status_code,302)
        response = self.c.get('/audio/'+str(song.id))

        #logging.info(response.content)
        self.failUnless('people was created</li>' in response.content)
        #logging.info(response.content)


    def test_artist_page(self):
        f = open(self.files[0])
        response = self.c.post('/drop', { 'file': f, 
                                         'accept': True,
                                        }) 
 
        self.failUnlessEqual(response.status_code, 302)
        logging.info(u'to test artist, posted a file again...')
        artist = Artist.objects.filter(name__contains='Baraka')[0]

        logging.info(u'found our new artist!')
        response = self.c.get('/artist/'+str(artist.id))
        #logging.info(response.request)
        self.failUnlessEqual(response.status_code, 200)
        self.assertTrue('<h2>add related tags</h2>' in  response.content)
        self.assertTrue('unclassifiable' in  response.content)
        logging.info(u'related tags for artist are working!' )

    '''    
    def test_locales(self):
        response = self.c.get('/')
        logging.info(u'changing language')
        response.request['Content-Language'] = 'es'

        response = self.c.get('/')
        logging.info(u'language changed? %s' % response.context )
    '''
        
    def test_tag_page(self):

        response = self.c.get('/tag/3')
        self.failUnlessEqual(response.status_code, 200)
        #logging.info(response)
        self.assertTrue('tag' in  response.content)

    def test_drop_page_error_messages(self):
        f = open(os.path.join(CURPATH, 'fixtures/genre_tag_missing.ogg'))
        response = self.c.post('/drop', { 'file': f, 'accept': True,
                            'csrfmiddlewaretoken': '02b2f45d81d9b6e0ba3e1e0fc02aa9ba'
                                         }) 
        #response = self.c.get('/tag/3/')
        self.failUnless('genre tag missing' in response.content)
        self.failUnlessEqual(response.status_code,200)
        f.close()

    def test_drop_an_audio_success(self):
        f = open(os.path.join(CURPATH, 'fixtures/Amiri_Baraka-Dope.ogg'))
        response = self.c.post('/drop', { 'file': f, 'accept': True,
                    'csrfmiddlewaretoken':'02b2f45d81d9b6e0ba3e1e0fc02aa9ba'

                                        })
        #logging.info(response)
        self.failUnless(response.status_code,200)
        logging.info(u'posted new file at the drop page')
        f.close()
        
        song =Song.objects.filter(title='Dope')[0]
        self.assertTrue(song.artist.name == 'Amiri Baraka')
        logging.info(u'song found: %s' % song)

        response = self.c.get('/audio/'+str(song.id))
        #logging.info(response)
        self.assertTrue(response.status_code,200)
        self.assertTrue('artist' in  response.content)
        self.assertTrue('Amiri Baraka' in  response.content)



    def test_one_playlist(self):
        '''operations with one playlist'''

        folder = os.path.join(CURPATH, 'fixtures/')
        newsongs = import_songs_from_folder(folder)

        self.assertTrue(len(newsongs)==2)
        #logging.info(newsongs)
        self.assertTrue('genre tag missing' in newsongs.values())
        self.assertTrue('artist tag missing' in newsongs.values())



        response = self.c.post('/pls/add', 
                    { 'songlist': [x.id for x in Song.objects.all()[:3]], 
                                'playlist': 'new'})

        self.failUnlessEqual(response.status_code, 302)
        logging.info('created playlist')


        response = self.c.get('/pls/1')
        self.assertTrue('you are logged in as test' in response.content)
        self.assertTrue('a new playlist has been created' in  response.content)


        self.assertTrue('Songlist' in  response.content)
        #self.assertTrue('<li><a href="/audio/4592">' in  response.content)
        self.assertTrue('<input type="submit" value="unclassifiable"' in  response.content)
        logging.info(u'related tags are working for playlists!')
        self.failUnlessEqual(response.status_code, 200)

        response = self.c.post('/pls/1', 
                    { 
                        'tag': 'peace',
                        'playlist_id': 1,
                    })

        self.failUnlessEqual(response.status_code, 302)
        response = self.c.get('/pls/1')
        self.assertTrue('tag peace added to playlist' in  response.content)
        self.assertTrue('tag peace created' in  response.content)
        logging.info(u'playlist tag created!')



        first_pls = Playlist.objects.get(pk=1)

        baraka = Song.objects.filter(title="Dope")[0]
        self.failUnlessEqual(baraka.artist.name,'Amiri Baraka')

        newentry = Entry(playlist=first_pls,song=baraka,position=4)
        newentry.save()

        logging.info(u'created a new entry in the playlist: %s' % newentry)
        response = self.c.get('/pls/1')

        self.assertTrue('Amiri Baraka' in  response.content)
        self.assertTrue(' value="unclassifiable"' in  response.content)
        self.assertTrue('<form method="POST" action="/pls/entry/2/delete">' in  response.content)



        response = self.c.get('/pls/1/pls')
        logging.info(u'pls file content type: %s' % response['Content-Type'])

        self.failUnlessEqual(response['Content-Type'] ,'audio/x-scpls' )


    def test_one_tag(self):

        folder = os.path.join(CURPATH, 'fixtures/')
        newsongs = import_songs_from_folder(folder)

        logging.info(u'imported songs errors: %s' % newsongs)
        self.assertTrue('artist tag missing' in  newsongs.values())
        self.assertTrue('genre tag missing' in  newsongs.values())
        othertag =  Tag.objects.get(tag='unclassifiable')
        logging.info(u'tag found!')
        response = self.c.get('/tag/'+str(othertag.id))
        #logging.info(u'response: %s' % response.content)


        self.assertTrue('<b>Dope</b> by Amiri Baraka' in  response.content)
        logging.info(u'song with tag found!')
        

    def test_requests(self):

        response = self.c.get('/requests')

        
        self.assertTrue('<h2>Playlists</h2>' in  response.content)
        self.assertTrue('<h2>Alive</h2>' in  response.content)
        self.failUnlessEqual(response.status_code,200)
        logging.info(u'/requests page status code: %s' % response.status_code)



    def test_skipcurrent(self):

        response = self.c.get('/skipcurrent')
        self.failUnlessEqual(response.status_code,302)

        response = self.c.get('/')
        self.failUnlessEqual(response.status_code,200)
        logging.info(u'/skipcurrent page status code: %s' % response.status_code)
        
        #logging.info(  response.content)
        self.assertTrue('<li class="success">' in  response.content)
        self.assertTrue('<h2>last songs</h2>' in  response.content)
        self.assertTrue('<li class="success"> song has been skipped</li>' in  response.content)
        logging.info(u'/skipcurrent has been performed!' )









































