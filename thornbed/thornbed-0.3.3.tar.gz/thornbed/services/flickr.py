from oembed import Consumer, NoEndpointError, NotFoundError
import re


def lookup(url, **kwargs):
    consumer = Consumer(
        [
            ('http://*.flickr.com/*', 'http://www.flickr.com/services/oembed/'),
        ]
    )
    try:
        res = consumer.lookup(url, **kwargs)
    except NoEndpointError, NotFoundError:
        res = None

    # since our friends at flickr do not return the thumbnail_url,
    # we will hack it ourselves, thumbnails are always in .jpg format
    # http://www.flickr.com/services/api/misc.urls.html
    if res:
        sre = re.search('_[mstzb].(jpg|gif|png)', url)
        if sre:
            thumb_url = '%s_t.jpg' % url[:sre.start()]
        else:
            thumb_url = '%s_t.jpg' % res['url'][:-4]

        res['thumbnail_url'] = thumb_url

    return res