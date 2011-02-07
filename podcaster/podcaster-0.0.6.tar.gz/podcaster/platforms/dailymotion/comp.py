# -*- coding:utf-8 -*-

import json
import re
import urllib
import restkit
from datetime import datetime

from podcaster.lib.podcast import BasePodcast, VideoFeed, UserFeed, VideoDetails, VideoFormat

class Safari(urllib.FancyURLopener):
    """Fake user agent"""
    version = "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_6; fr-fr) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4"

class DMPodcast(BasePodcast):
    VIDEO_FORMATS = (
        VideoFormat('1', 'MP4 848x480', 'mp4', 'video/mp4', 1),
        VideoFormat('2', 'MP4 1280x720', 'mp4', 'video/mp4', 1)
    )
    PREFERED_FORMAT = '1'
    PREFIX = 'dm'
    PLATFORM_NAME = 'Dailymotion'
    LOGO = 'img/logo_dailymotion.png'

    def get_user_feed(self, username, max_results=25):
        ress = restkit.Resource("https://api.dailymotion.com")
        try:
            resp = ress.get("/videos", user=username, fields='id,title,created_time,modified_time,duration,description').body_string()
        except restkit.errors.RequestFailed:
            # Not found
            return None
        data = json.loads(resp)

        if not data['list'] and not data['has_more']:
            # No data == no channel
            return None

        videos = []
        feed_title = username
        feed_description = '%s on Dailymotion' % username
        for v in data['list']:
            id = v['id']
            title = v['title']
            guid = '%s:%s' % (username, id)
            published = datetime.fromtimestamp(float(v['created_time']))
            updated = datetime.fromtimestamp(float(v['modified_time']))
            duration = int(v['duration'])
            description = v['description']
            videos.append(VideoFeed(id, guid, title, description, published, updated, duration))

        return UserFeed(username, feed_title, feed_description, videos)

    def get_video_details(self, id):
        ress = restkit.Resource("https://api.dailymotion.com")
        resp = ress.get('/video/%s' % id, fields='url').body_string()
        data = json.loads(resp)
        url = data['url']

        s = Safari().open(url).read()
        regex = re.compile('''so_player_(\w+)\.addVariable\("sequence",\s*"(.*)"\);''')
        m = regex.search(s)
        js = m.group(2)
        js = urllib.unquote_plus(unicode(js, 'utf-8')).replace("\\'", "'")

        # H264-848x480
        hqurl = re.search('''"hqURL":"([^""]+)"''', js).group(1).replace('\\', '')
        # H264-1280x720
        hdurl = re.search('''"hdURL":"([^""]+)"''', js).group(1).replace('\\', '')

        return VideoDetails(id, {'1': hqurl, '2': hdurl})





