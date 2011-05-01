# encoding: utf-8
"""
The AJAX code generate by the template tag (see
:mod:`lastfm.templatetags.lastfm_widget`) doesn’t contact Last.fm directly,
but uses a Django view as proxy. The advantage of this is, that you can
exactly control what data your site gets. Another advantage is, that visitors
can’t see your Last.fm username by inspecting the HTML source of your site.

In addition to the view itself this module also defines some helper classes
that are responsible for handling the different types of charts (e.g. top
tracks or top artists).

"""
import urllib

from django.conf import settings
from django.http import HttpResponse
from django.utils import simplejson as json
from django.views.decorators.cache import cache_page


URL = 'http://ws.audioscrobbler.com/2.0/?'

LASTFM_USER = getattr(settings, 'LASTFM_USER', '')
LASTFM_API_KEY = getattr(settings, 'LASTFM_API_KEY', '')
LASTFM_SECRET = getattr(settings, 'LASTFM_SECRET', '')
LASTFM_CHART_TYPE = getattr(settings, 'LASTFM_CHART_TYPE', 'top_artists')
LASTFM_WIDGET_TITLE = getattr(settings, 'LASTFM_WIDGET_TITLE',
        'Weekly Top Artists')
LASTFM_NUM_IMAGES = getattr(settings, 'LASTFM_NUM_IMAGES', '12')
LASTFM_TOP_ARTISTS_PERIOD = getattr(settings, 'LASTFM_TOP_ARTISTS_PERIOD',
        '7day')
LASTFM_IMG_SIZE = getattr(settings, 'LASTFM_IMG_SIZE', 'large')


@cache_page(60 * 5)
def lastfm_data(request):
    """
    This view retrievs the data from Last.fm and returns a JSON encoded list.
    The template tag’s AJAX code will retrieve this list and generate the
    chart from it.

    Each list entry is a dict with three elements:
     * ``title``: Contains the song title or artist name and can be displayed
       as alternative text or link title.
     * ``url``: A url pointing to the track or artist on Last.fm.
     * ``img_url``: A url pointing to the track’s cover or artist image.

    For each chart type there is a class that handles its data. They are
    necessary to unify Last.fm’s different key names to those three explained
    above. Currently, there is no abstract base class which they must inherit
    from, but each class is expected to implement the following attributes and
    methods:

    ``params``: A dict that contains all parameters required by the `Last.fm
    API call <http://www.lastfm.de/api>`_

    ``get_data(data)``: Last.fm’s JSON data is quite nested. This method
    should extract the list with the actual items from the raw data.

    ``get_item_title(item)``: Return an item’s text for the ``title``
    attribute in the data dict.

    ``get_default_image()``: Return a url to a default image that will be used
    if a track or artist has no image on its own.

    ``get_img_url(img_size, item)``: This method needs to be implemented only
    if an item has no ``image`` key (which is the case for e.g. the weekly top
    artist). It gets the desired image size (small, medium, large, …) and the
    item. It might do another API call and extract a custom image URL for that
    item.

    """
    chart_types = {
        'recent_tracks': RecentTracks,
        'weekly_top_artists': WeeklyTopArtists,
        'top_artists': TopArtists,
    }
    img_size = LASTFM_IMG_SIZE

    chart = chart_types[LASTFM_CHART_TYPE]()

    try:
        params = urllib.urlencode(chart.params)
        data = json.loads(urllib.urlopen(URL + params).read())

        if 'error' in data:
            raise RuntimeError(str(data))

        data = chart.get_data(data)
        if not data:
            raise IOError('No artists found.')
        elif type(data) == dict:
            data = [data]
    except (IOError, ValueError):
        return HttpResponse(json.dumps([]), mimetype='application/json')

    items = []
    for i, d in enumerate(data):
        # Not every last.fm method supports the ``limit`` parameter so we have
        # to take care of this ourselves.
        if i == int(LASTFM_NUM_IMAGES):
            break

        item = {
            'title': chart.get_item_title(d),
            'url': d['url'],
            'img_url': chart.get_default_image(),
        }

        if 'image' in d:
            for img in d['image']:
                if img['size'] == img_size and img['#text']:
                    item['img_url'] = img['#text']
                    break
        else:
            item['img_url'] = chart.get_img_url(img_size, d)

        items.append(item)

    return HttpResponse(json.dumps(items), mimetype='application/json')


class RecentTracks(object):
    """This class handles the API call ``user.getRecentTracks``."""
    params = {
        'method': 'user.getRecentTracks',
        'user': LASTFM_USER,
        'limit': LASTFM_NUM_IMAGES,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
    }

    def get_data(self, data):
        return data['recenttracks']['track']

    def get_item_title(self, item):
        return u'%s – %s' % (item['artist']['#text'], item['name'])

    def get_default_image(self):
        return 'http://cdn.last.fm/depth/catalogue/noimage/cover_85px.gif'


class WeeklyTopArtists(object):
    """This class handles the API call ``user.getWeeklyArtistChart``."""
    params = {
        'method': 'user.getWeeklyArtistChart',
        'user': LASTFM_USER,
        'limit': LASTFM_NUM_IMAGES,
        'api_key': LASTFM_API_KEY,
        'format': 'json',
    }

    def get_data(self, data):
        return data['weeklyartistchart']['artist']

    def get_item_title(self, item):
        return '%s (%s plays)' % (item['name'], item['playcount'])

    def get_default_image(self):
        return 'http://cdn.last.fm/flatness/catalogue/noimage/2/' + \
                'default_artist_large.png'

    def get_img_url(self, img_size, item):
        """
        A chart item of this class does not contain any images, so we need to
        do another API call to get an image for artist in ``item``.

        """
        params = urllib.urlencode({
            'method': 'artist.getimages',
            'artist': item['name'],
            'limit': 1,
            'api_key': LASTFM_API_KEY,
            'format': 'json',
        })

        try:
            img_data = json.loads(urllib.urlopen(
                    URL + params).read())['images']
        except (IOError, ValueError):
            return ''

        fallback = ''
        if 'image' in img_data:
            img_data = img_data['image']['sizes']['size']
            for img in img_data:
                fallback = img['#text']
                if img['name'] == img_size and img['#text']:
                    return img['#text']
        return fallback


class TopArtists(object):
    """
    This class handles the API call ``user.getTopArtists``. The period must be
    defined in the site’s settings module.

    """
    params = {
        'method': 'user.getTopArtists',
        'user': LASTFM_USER,
        'api_key': LASTFM_API_KEY,
        'period': LASTFM_TOP_ARTISTS_PERIOD,
        'format': 'json',
    }

    def get_data(self, data):
        return data['topartists']['artist']

    def get_item_title(self, item):
        return '%s (%s plays)' % (item['name'], item['playcount'])

    def get_default_image(self):
        return 'http://cdn.last.fm/flatness/catalogue/noimage/2/' + \
                'default_artist_large.png'
