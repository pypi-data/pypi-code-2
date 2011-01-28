# -*- coding:utf-8 -*-
import json
import re
import collections
from urllib import unquote_plus
from nagare.namespaces import xhtml, xml
from podcaster.lib.dates import parse_date


VideoFeed = collections.namedtuple('VideoFeed', 'id,guid,title,published,updated')
UserFeed = collections.namedtuple('UserFeed', 'username,videos')


def get_user_feed(username, max_results=25):
    root = xml.XmlRenderer().parse_xml('http://gdata.youtube.com/feeds/api/users/%s/uploads?v=2&max-results=%d' % (username, max_results))
    nsmap = root.nsmap
    if 'yt' not in nsmap or 'media' not in nsmap:
        return None

    ns = nsmap[None] #Default namespace is Atom
    nsyt = nsmap['yt'] #YouTube namespace
    nsmedia = nsmap['media'] #Media namespace

    videos = []
    for vtag in root.findall('{%s}entry' % ns):
        guid = vtag.find('{%s}id' % ns).text
        published = parse_date(vtag.find('{%s}published' % ns).text)
        updated = parse_date(vtag.find('{%s}updated' % ns).text)
        title = vtag.find('{%s}title' % ns).text
        id = vtag.find('{%s}group/{%s}videoid' % (nsmedia, nsyt)).text
        videos.append(VideoFeed(id, guid, title, published, updated))
    return UserFeed(username.lower(), videos)


VideoDetails = collections.namedtuple('VideoDetails', 'id,urls')


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
            urls = {}
            for format_id, quoted_url in [u.split('|') for u in params['args']['fmt_url_map'].split(',')]:
                urls[format_id] = unquote_plus(quoted_url)
            break
    return VideoDetails(id, urls)
