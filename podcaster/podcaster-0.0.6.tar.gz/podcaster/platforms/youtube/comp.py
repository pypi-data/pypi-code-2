# -*- coding:utf-8 -*-

import json
import re
from urllib import unquote_plus
from nagare.namespaces import xml, xhtml

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

    def get_video_details(self, id):
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
                urls = {}
                for format_id, quoted_url in [u.split('|') for u in params['args']['fmt_url_map'].split(',')]:
                    urls[format_id] = unquote_plus(quoted_url)
                break
        return VideoDetails(id, urls)

