# -*- coding:utf-8 -*-
import json
import re
import collections
from urllib import unquote_plus
from nagare.namespaces import xhtml
from webob.exc import HTTPBadRequest
from gdata.youtube.service import YouTubeService
from podcaster.lib.dates import parse_date


def get_user_feed(username, max_results=25):
    """Downloads the videos uploaded by given user"""
    svc = YouTubeService()
    uri = 'http://gdata.youtube.com/feeds/api/users/%s/uploads?start-index=1&max-results=%d' % (username, max_results)
    try:
        return UserFeed(svc.GetYouTubeVideoFeed(uri))
    except Exception, e:
        raise HTTPBadRequest(explanation=str(e))


VideoFeed = collections.namedtuple('VideoFeed', 'id,title,published,updated')


class UserFeed(object):
    def __init__(self, feed):
        self.title = unicode(feed.title.text, 'utf-8')
        self.url = ''
        for link in feed.link:
            if link.rel == 'alternate':
                self.url = link.href
                break
        self.init_videos(feed)

    def init_videos(self, feed):
        self.videos = []
        for entry in feed.entry:
            title = unicode(entry.title.text, 'utf-8')
            published = parse_date(entry.published.text)
            updated = parse_date(entry.updated.text)
            id = entry.id.text.split('/')[-1]
            v = VideoFeed(id, title, published, updated)
            self.videos.append(v)

VideoDetails = collections.namedtuple('VideoDetails', 'id,title,urls')

def get_video_details(id):
    """Returns the available video formats"""
    url = "http://www.youtube.com/watch?v=%s" % id
    root = xhtml.Renderer().parse_html(url)
    regex = re.compile(r"""swfConfig = (.*);""")
    urls = {}
    for script in root.findall('.//script'):
        if not script.text: continue
        m = regex.search(script.text)
        if m:
            params = json.loads(m.group(1))
            urls = dict([(k, unquote_plus(v)) for k, v in [u.split('|') for u in params['args']['fmt_url_map'].split(',')]])
            break
    return VideoDetails(id, 'todo', urls)
