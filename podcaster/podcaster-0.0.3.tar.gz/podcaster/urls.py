# -*- coding:utf-8 -*-
from nagare import presentation
from webob.exc import HTTPTemporaryRedirect, HTTPOk

from podcaster.comp import Main
from podcaster.lib.video_formats import get_format, PREFERED_FORMAT
from podcaster.lib.rss_renderer import RssRenderer
from podcaster.lib.youtube import get_user_feed, get_video_details
from podcaster.lib.dates import rfc2822


@presentation.init_for(Main, 'len(url) >= 2 and url[0]=="user"')
def init(self, url, comp, http_method, request):
    name = url[1]
    format = get_format(url[2] if len(url) >= 3 else PREFERED_FORMAT)
    feed = get_user_feed(name)
    r = RssRenderer()
    with r.rss(version='2.0'):
        with r.channel:
            r << r.title('Videos by %s (%s)' % (name, format.description))
            r << r.link('http://www.youtube.com/user/%s' % name)
            for v in feed.videos:
                with r.item:
                    r << r.title(v.title)
                    r << r.guid("%s:%s" % (name, v.id))
                    r << r.link('http://www.youtube.com/watch?v=%s' % v.id)
                    r << r.pubDate(rfc2822(v.published))
                    r << r.enclosure(url=request.relative_url('video.%s?id=%s&fmt=%s' % (format.extension, v.id, format.id), to_application=True),
                                     length=10,
                                     type=format.content_type)
    raise HTTPOk(body=r.root.write_xmlstring(xml_declaration=True, encoding='utf-8', pretty_print=True),
                 content_type='text/xml')


@presentation.init_for(Main, 'len(url) == 1 and url[0].startswith("video.")')
def init(self, url, comp, http_method, request):
    video_id = request.params.get('id')
    format_id = request.params.get('fmt', PREFERED_FORMAT)
    details = get_video_details(video_id)
    raise HTTPTemporaryRedirect(location=details.urls[format_id])
