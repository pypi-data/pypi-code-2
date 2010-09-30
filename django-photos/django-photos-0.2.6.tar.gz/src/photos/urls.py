from photos.views import album_list, photo_list, photo_detail
from django.views.generic.list_detail import object_detail
from django.conf.urls.defaults import *
from photos.models import Photo, Album

ALBUM_DETAIL_DICT = {'queryset': Album.objects.filter(display=True)}
PHOTO_DETAIL_DICT = {'queryset': Photo.objects.filter(display=True)}

urlpatterns = patterns('',
    url(r'^albums/$', album_list, name='albums'),
    url(r'^albums/(?P<user_id>\d+)/$', album_list, name='albums-userid'),
    url(r'^albums/(?P<username>.+)/$', album_list, name='albums-username'),
    url(r'^album/(?P<object_id>\d+)/$', object_detail, ALBUM_DETAIL_DICT, name='album-detail'),
    url(r'^photos/$', photo_list, name='photos'),
    url(r'^photos/(?P<user_id>\d+)/$', photo_list, name='photos-userid'),
    url(r'^photo/(?P<object_id>\d+)/$', object_detail, PHOTO_DETAIL_DICT, name='photo-detail'),
    url(r'^photos/(?P<album_id>\d+)/(?P<object_id>\d+)/$', photo_detail, PHOTO_DETAIL_DICT, name='photo-album-detail'),
    url(r'^photos/(?P<username>.+)/', photo_list, name='photos-username')
)
