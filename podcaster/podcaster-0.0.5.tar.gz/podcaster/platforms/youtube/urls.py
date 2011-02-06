# -*- coding:utf-8 -*-

from webob.exc import HTTPOk, HTTPClientError, HTTPTemporaryRedirect
from nagare import presentation

from podcaster.lib.renderers import RssRenderer, ItunesRenderer
from podcaster.lib.dates import rfc2822
from comp import YTPodcast

@presentation.init_for(YTPodcast, 'len(url) >= 2 and url[0]=="user"')
def init(self, url, comp, http_method, request):
    name = url[1]
    format = self.choose_format(url[2] if len(url) >= 3 else None)
    feed = self.get_user_feed(name)
    r = RssRenderer()
    r.namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    i = ItunesRenderer(r)
    i.default_namespace = 'itunes'

    with r.rss(version='2.0'):
        with r.channel:
            r << r.title(u'%s (%s)' % (feed.title, format.description))
            r << r.link('http://www.youtube.com/user/%s' % name)
            for v in feed.videos:
                with r.item:
                    r << r.title(v.title)
                    r << r.guid("%s:%s" % (name, v.id))
                    r << r.link('http://www.youtube.com/watch?v=%s' % v.id)
                    r << r.pubDate(rfc2822(v.updated))
                    r << r.enclosure(url=request.relative_url('%s/video.%s?id=%s&fmt=%s' % (self.PREFIX, format.extension, v.id, format.id), to_application=True),
                                     length=10,
                                     type=format.content_type)
    raise HTTPOk(body=r.root.write_xmlstring(xml_declaration=True, encoding='utf-8', pretty_print=True),
                 content_type='text/xml')


@presentation.init_for(YTPodcast, 'url and url[0].startswith("video.")')
def init(self, url, comp, http_method, request):
    video_id = request.params.get('id')
    format = self.choose_format(request.params.get('fmt', None))
    if format is None:
        raise HTTPClientError(body='No suitable video format found')
    details = self.get_video_details(video_id)
    location = ''
    if format.id in details.urls:
        location = details.urls[format.id]
    else:
        for res in self.get_lower_resolutions(format):
            if res.id in details.urls:
                location = details.urls[res.id]
                break
    if location:
        raise HTTPTemporaryRedirect(location=location)
    else:
        raise HTTPClientError(body='Could not find the requested video (%s) using specified format or lower resolutions.' % video_id)
