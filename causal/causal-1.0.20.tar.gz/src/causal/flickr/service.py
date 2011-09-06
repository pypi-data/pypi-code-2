"""This file provides the fetching and converting of the
feed from flickr.com.
"""

from causal.main.handlers import OAuthServiceHandler
from causal.main.models import ServiceItem
from causal.main.exceptions import LoggedServiceError
from datetime import datetime, timedelta
from django.utils import simplejson
import flickrapi
import time
from oauth2 import Consumer, Token, Client

class ServiceHandler(OAuthServiceHandler):
    display_name = 'Flickr'

    def _get_username(self):
        """Fetch username from flickr"""
        profile = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.urls.getUserProfile&format=json&nojsoncallback=1')
        
        if not profile['stat'] == 'ok':
            return
        else:
            return profile['user']['nsid']
    
    def get_items(self, since):
        """Fetch and normalise the updates from the service.
        """
        # http://api.flickr.com/services/rest/?method=flickr.people.getPhotos&api_key=123&user_id=50685137%40N00&format=json&nojsoncallback=1&auth_token=123&api_sig=123
        # http://www.flickr.com/services/api/explore/flickr.people.getPhotos
        
        user_id = self._get_username()
        if not user_id:
            return
        
        photos = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.people.getPhotos&user_id=%s&format=json&nojsoncallback=1&min_upload_date=%s' % (user_id, since.strftime('%Y-%m-%d+%H:%M:%S')))
        items = []
        if photos and int(photos['photos']['total']) > 0:
            for photo in photos['photos']['photo']:
                # Info about the pic
                #pic = self.flickr.photos_getInfo(photo_id=photo['id'], format='json', nojsoncallback='1')
                
                pic_json = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.photos.getInfo&user_id=%s&format=json&nojsoncallback=1&photo_id=%s' % (user_id, photo['id']))

                item = ServiceItem()

                item.title = pic_json['photo']['title']['_content']
                item.body = pic_json['photo']['description']['_content']
                # Use date from when the photo was uploaded to flickr NOT when it was taken
                item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'

                item.link_back = pic_json['photo']['urls']['url'][0]['_content']
                item.tags = pic_json['photo']['tags']['tag']
                item.favorite = pic_json['photo']['isfavorite']

                item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.body = '<br/><img src="%s" />' % (item.url_thumb,)
                item.service = self.service

                items.append(item)
        return items

    def _fetch_favorites(self):
        """Fetch the list of photos that the current use has made their fav.
        """

        delta = timedelta(days=7)
        now = datetime.now()
        then = now - delta
        epoch_now = time.mktime(now.timetuple())
        epoch_then = time.mktime(then.timetuple())

        favs = self.flickr.favorites_getList(
            user_id=self.service.auth.secret,
            max_fave_date=int(epoch_now),
            min_fave_date=int(epoch_then),
            format='json',
            nojsoncallback ='1'
        )

        return simplejson.loads(favs)

    def get_stats_items(self, since):
        """Fetch and normalise the updates from the service and generate stats.
        """

        user_id = self._get_username()
        if not user_id:
            return
        
        photos = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.people.getPhotos&user_id=%s&format=json&nojsoncallback=1&min_upload_date=%s' % (user_id, since.strftime('%Y-%m-%d+%H:%M:%S')))

        items = []

        if photos and int(photos['photos']['total']) > 0:
            for photo in photos['photos']['photo']:

                item = ServiceItem()

                # Info about the pic
                pic_json = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.photos.getInfo&user_id=%s&format=json&nojsoncallback=1&photo_id=%s' % (user_id, photo['id']))

                # Info about how the pic was taken
                exif_json = self._get_oauth_v1('http://api.flickr.com/services/rest/?method=flickr.photos.getExif&user_id=%s&format=json&nojsoncallback=1&photo_id=%s' % (user_id, photo['id']))
                item.camera_make, item.camera_model = self._extract_camera_type(exif_json)
                item.title = pic_json['photo']['title']['_content']
                item.body = pic_json['photo']['description']['_content']

                # Use date from when the photo was uploaded to flickr NOT when it was taken
                item.created = datetime.fromtimestamp(float(pic_json['photo']['dates']['posted'])) #u'posted': u'1300054696'

                item.link_back = pic_json['photo']['urls']['url'][0]['_content']
                item.tags = pic_json['photo']['tags']['tag']
                item.favorite = pic_json['photo']['isfavorite']

                # Add views
                item.views = pic_json['photo']['views']

                # Add tags
                item.tags = pic_json['photo']['tags']['tag']

                item.number_of_comments = pic_json['photo']['comments']['_content']

                item.url_thumb = "http://farm%s.static.flickr.com/%s/%s_%s_t.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.url_small = "http://farm%s.static.flickr.com/%s/%s_%s_m.jpg" % (
                    pic_json['photo']['farm'],
                    pic_json['photo']['server'],
                    pic_json['photo']['id'],
                    pic_json['photo']['secret']
                )

                item.body = '<br/><img src="%s" />' % (item.url_thumb,)

                # Add location
                item.location = {}
                if pic_json['photo'].has_key('location'):
                    item.location['lat'] = pic_json['photo']['location']['latitude']
                    item.location['long'] = pic_json['photo']['location']['longitude']

                item.service = self.service

                items.append(item)
        return items

    def _extract_camera_type(self, json):
        """Return the make and model of a photo.
        """

        make = 'Unknown make'
        model = 'Unknown model'
        
        try:
            for exif in json['photo']['exif']:
                if exif['label'] == 'Make':
                    make = exif['raw']['_content']
                elif exif['label'] == 'Model':
                    model = exif['raw']['_content']
        except:
            pass

        return make, model
