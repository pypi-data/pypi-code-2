""" Imgur data processor

    Since Imgur doesn't provide oEmbed interface, we have to query data using
    their API, so this is a Wrapper for their API service.

    http://imgur.com/gallery/NiK0X
    http://imgur.com/BynR8
    http://i.imgur.com/BynR8.png
    http://i.imgur.com/BynR8s.png

    images can be png, jpg or gif

    json returned by imgur

    {
        "image":
            {
                "image": {
                            "title": null,
                            "caption": null,
                            "hash": "BynR8",
                            "datetime": "2011-08-30 23:45:13",
                            "type": "image\/jpeg",
                            "animated": "false",
                            "width": 500,
                            "height": 578,
                            "size": 75375,
                            "views": 358449,
                            "bandwidth": 27018093375
                            },
                "links": {
                            "original": "http:\/\/i.imgur.com\/BynR8.jpg",
                            "imgur_page": "http:\/\/imgur.com\/BynR8",
                            "small_square": "http:\/\/i.imgur.com\/BynR8s.jpg",
                            "large_thumbnail": "http:\/\/i.imgur.com\/BynR8l.jpg"
                         }
            }
    }
    
"""
import re
from urllib2 import urlopen, HTTPError
import simplejson as json

imgur_endpoint = 'http://api.imgur.com/2/image/%s.json'

def lookup(url, **kwargs):
    # we are planning to support albums in a near future, not for now
    if not re.search('(i\.)?imgur.com', url) or re.search('imgur.com\/a\/', url):
        return None
    gallery = re.search('gallery', url)
    direct_link = re.search('\/(\w)*[^s](\.gif|\.jpg|\.png)$', url)
    thumb = re.search('\/(\w)*s(\.gif|\.jpg|\.png)$', url)

    if gallery or not (direct_link or thumb):
        pic_id = re.search('\/(\w)*$', url).group()[1:]
    elif thumb:
        pic_id = thumb.group()[1:-5]
    elif direct_link:
        pic_id = direct_link.group()[1:-4]
    else:
        raise ValueError("Can't parse your URL %s" % url)

    try:
        buf = urlopen(imgur_endpoint % pic_id).read()
    except HTTPError:
        return None
    data = json.loads(buf)
    if 'error' in data:
        # TODO: has oEmbed any kind of error status?
        return None

    res = {
        'type': 'photo',
        'version': '1.0',
        'provider_name': 'imgur.com',
        'provider_url': 'http://imgur.com',
        'thumbnail_url': data['image']['links']['small_square'],
        'imgur_page': data['image']['links']['imgur_page'],
        'url': data['image']['links']['original'],
        'width': data['image']['image']['width'],
        'height': data['image']['image']['height'],
        'datetime': data['image']['image']['datetime'],
        'views': data['image']['image']['views'],
        'title': data['image']['image']['title'],
        }

    return res
