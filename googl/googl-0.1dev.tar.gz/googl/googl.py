import httplib2
from apiclient.discovery import build
from restfulie import Restfulie
from short_url import ShortUrl

GOOGL_API_URL = 'https://www.googleapis.com/urlshortener/v1/url'

class Googl(object):

    @classmethod
    def oauth(cls, oauth_storage):
        cls._oauth_storage = oauth_storage
        return cls

    @classmethod
    def shorten(cls, url):
        data = {'longUrl':url}
        try:
            getattr(cls, '_oauth_storage')
        except AttributeError:
            response = Restfulie.at(GOOGL_API_URL).as_('application/json').post(data)
            return ShortUrl(response.body)
        else:
            return cls._oauth_action('insert', cls._oauth_storage, {'body':data})

    @classmethod
    def expand(cls, short_url):
        try:
            getattr(cls, '_oauth_storage')
        except AttributeError:
            response = Restfulie.at(GOOGL_API_URL + '?shortUrl=%s' % short_url).get()
            return ShortUrl(response.body)
        else:
            return cls._oauth_action('get', cls._oauth_storage, {'shortUrl':short_url})

    @classmethod
    def _oauth_action(cls, action, oauth_storage, parameter):
        http = httplib2.Http()
        credentials = oauth_storage.get()
        http = credentials.authorize(http)
        service = build('urlshortener','v1',http=http)
        url = service.url()
        response = getattr(url, action)(**parameter).execute()
        del cls._oauth_storage
        return response

    @classmethod
    def analytics(cls, short_url):
        response = Restfulie.at(GOOGL_API_URL + '?shortUrl=%s&projection=FULL' % short_url).get()
        return ShortUrl(response.body)

