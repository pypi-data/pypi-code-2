from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from photos.models import Photo, Album

class TemplateTagTest(TestCase):
    pass

class ViewTest(TestCase):
    def setUp(self):
        user, created = User.objects.get_or_create(username='anna')
        album = Album()
        album.user = user
        album.save()
        photo1 = Photo(photo='a.jpg')
        photo1.user = user
        photo1.save()
        
        photo2 = Photo(photo='b.jpg')
        photo2.user = user
        photo2.save()
        
        album.photos.add(photo1)
        album.photos.add(photo2)
        album.save()        
    
    def check_url(self, url, status_code=200):
        client = Client()
        response = client.get(url)
        msg = '%s != %s in %s' % (response.status_code, status_code, url)
        self.assertEqual(response.status_code, status_code, msg)
    
    def test_album_list(self):
        url = reverse('albums')
        self.check_url(url, 200)
        
    def test_album_list_userid(self):
        user = User.objects.latest('id')
        url = reverse('albums-userid', args=(user.id, ))
        self.check_url(url, 200)
        
    def test_album_list_username(self):
        user = User.objects.latest('id')
        url = reverse('albums-username', args=(), kwargs={'username': user.username})
        self.check_url(url, 200)
        
    def test_album_detail(self):
        album = Album.objects.latest('id')
        url = reverse('album-detail', args=(album.id, ))
        self.check_url(url, 200)
        
    def test_photo_list(self):
        url = reverse('photos')
        self.check_url(url, 200)
        
    def test_photo_list_userid(self):
        user = User.objects.latest('id')
        url = reverse('photos-userid', args=(user.id, ))
        self.check_url(url, 200)
        
    def test_photo_list_username(self):
        user = User.objects.latest('id')
        url = reverse('photos-username', args=(), kwargs={'username': user.username})
        self.check_url(url, 200)
        
    def test_photo_detail(self):
        photo = Photo.objects.latest('id')
        url = reverse('photo-detail', args=(photo.id, ))
        self.check_url(url, 200)
        
    def test_photo_name(self):
        photo = Photo.objects.get(id=1)
        self.assertEqual(photo.name, 'a')
    