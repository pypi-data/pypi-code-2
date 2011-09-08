# -*- coding:utf-8 -*-

import re
from urllib import unquote_plus, quote_plus
from nagare.namespaces import xml, xhtml
from nagare import log
from urlparse import urlparse, urlunparse

from podcaster.lib.dates import parse_date
from podcaster.lib.podcast import BasePodcast, VideoFeed, UserFeed, VideoDetails, VideoFormat

class YTPodcast(BasePodcast):
    VIDEO_FORMATS = (
        VideoFormat('18', 'MP4 480x360', 'mp4', 'video/mp4', 1),
        VideoFormat('22', 'MP4 1280x720', 'mp4', 'video/mp4', 1),
        VideoFormat('37', 'MP4 1920x1080', 'mp4', 'video/mp4', 1),
        VideoFormat('38', 'MP4 4096x3072', 'mp4', 'video/mp4', 1),
    )
    PREFERED_FORMAT = '22'
    PREFIX = 'yt'
    PLATFORM_NAME = 'YouTube'
    LOGO = 'img/logo_youtube.png'

    def get_user_feed(self, username, max_results=25):
        root = xml.XmlRenderer().parse_xml('http://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&max-results=%d' % (username, max_results))
        nsmap = root.nsmap
        if 'yt' not in nsmap or 'media' not in nsmap:
            return None

        ns = nsmap[None] #Default namespace is Atom
        nsyt = nsmap['yt'] #YouTube namespace
        nsmedia = nsmap['media'] #Media namespace

        videos = []
        feed_title = username
        feed_description = '%s on YouTube' % username
        for vtag in root.findall('{%s}entry' % ns):
            guid = vtag.find('{%s}id' % ns).text
            published = parse_date(vtag.find('{%s}published' % ns).text)
            updated = parse_date(vtag.find('{%s}updated' % ns).text)
            title = vtag.find('{%s}title' % ns).text
            id = vtag.find('{%s}group/{%s}videoid' % (nsmedia, nsyt)).text
            duration = int(vtag.find('{%s}group/{%s}duration' % (nsmedia, nsyt)).get('seconds'))
            description = ''
            videos.append(VideoFeed(id, guid, title, description, published, updated, duration))
        return UserFeed(username.lower(), feed_title, feed_description, videos)

    def clean_url(self, u):
        u = re.sub('&itag=\d+', '', u, 1)
        o = urlparse(u)
        qs = dict([re.match('(.*?)=(.*)', e).groups() for e in o.query.split('&')])
        for param in ('type',):
            # Some params need quoting
            qs[param] = quote_plus(qs[param])
        query = '&'.join(['%s=%s' % (k, v) for k, v in qs.items()])
        u = urlunparse((o.scheme, o.netloc, o.path, o.params, query, o.fragment))
        return u

    def get_video_details(self, id):
        """Returns the available video formats"""
        url = "http://www.youtube.com/watch?v=%s" % id
        root = xhtml.Renderer().parse_html(url)
        embed = root.find('.//embed')
        fv = embed.get('flashvars')
        fv = dict([re.match('(.*?)=(.*)', e).groups() for e in fv.split('&')])
        #  unquote_plus(fv['fmt_list']) like
        # '37/1920x1080/9/0/115,45/1280x720/99/0/0,22/1280x720/9/0/115,44/854x480/99/0/0,35/854x480/9/0/115,43/640x360/99/0/0,34/640x360/9/0/115
        formats = [e.split('/')[0] for e in unquote_plus(fv['fmt_list']).split(',')]
        log.debug(formats)
        urls = [unquote_plus(unquote_plus(u)) for u in re.split(',?url=', unquote_plus(fv['url_encoded_fmt_stream_map'])) if u]

        # For some reason, urls contain param itag twice so we need to remove one
        urls = [self.clean_url(u) for u in urls]


        urls = dict(zip(formats, urls))
        return VideoDetails(id, urls)
