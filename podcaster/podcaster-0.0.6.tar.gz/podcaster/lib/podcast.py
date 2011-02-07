# -*- coding:utf-8 -*-
import collections
from webob.exc import HTTPOk, HTTPClientError, HTTPTemporaryRedirect, HTTPNotFound
from nagare import editor, validator, presentation
from podcaster.lib.dates import rfc2822
from podcaster.lib.renderers import RssRenderer, ItunesRenderer


VideoFeed = collections.namedtuple('VideoFeed', 'id,guid,title,description,published,updated,duration')
UserFeed = collections.namedtuple('UserFeed', 'username,title,description,videos')
VideoDetails = collections.namedtuple('VideoDetails', 'id,urls')
VideoFormat = collections.namedtuple('VideoFormat', 'id,description,extension,content_type,supported')


class BasePodcast(object):

    VIDEO_FORMATS = []
    PREFERED_FORMAT = None
    PREFIX = 'XXX'
    PLATFORM_NAME = 'unknown'
    LOGO = ''

    def __init__(self):
        self.username = editor.Property('').validate(self.validate_username)
        self.format = editor.Property(self.PREFERED_FORMAT)
        self.podcast_link = ''

    def validate_username(self, v):
        v = validator.StringValidator(v, strip=True).not_empty().to_string()
        if self.get_user_feed(v, max_results=1) is None:
            raise ValueError('No channel found for username "%s"' % v)
        return v

    def create_podcast_link(self):
        self.podcast_link = ''
        if not self.username.error:
            self.podcast_link = '%s/user/%s/%s' % (self.PREFIX, self.username.value, self.format.value)

    def get_user_feed(self, username, max_results=25):
        raise NotImplementedError()

    def get_video_details(self, id):
        raise NotImplementedError()

    def available_formats(self):
        return self.VIDEO_FORMATS

    def choose_format(self, fmt_id=None):
        for f in self.VIDEO_FORMATS:
            if f.id == fmt_id:
                return f
        return self.choose_format(self.PREFERED_FORMAT)

    def get_lower_resolutions(self, format):
        return reversed(self.VIDEO_FORMATS[:self.VIDEO_FORMATS.index(format)])


# -------------------------------------------------------------------------------
# Common renderer

@presentation.render_for(BasePodcast)
def render(self, h, comp, *args):
    with h.form:
        h << h.h2('Generate your podcast link')
        h << h.div('%s Username' % self.PLATFORM_NAME)
        h << h.input(value=self.username()).action(self.username).error(self.username.error) << ' '
        h << h.div('Choose desired format')
        with h.select.action(self.format):
            h << [h.option(f.description, value=f.id).selected(self.format()) for f in self.available_formats()]
        h << h.div('This is the prefered format for your podcast. If the desired format is not available, Podcaster will try lower resolutions automatically.', class_='field-description')
        h << h.div(h.input(type='submit', value='Get my link').action(self.create_podcast_link), class_='submit')
    if self.podcast_link:
        h << h.h2('Here is your link !')
        h << h.p('Click on this link to open this podcast directly with iTunes')
        abs_url = h.request.relative_url(self.podcast_link)
        itunes_url = abs_url.replace('http://', 'itpc://')
        h << h.div(h.a(h.img(src='img/logo_itunes.png'), ' ', itunes_url, href=itunes_url), class_='podcast-link')
    return h.root


# -------------------------------------------------------------------------------
# RSS Feed

@presentation.init_for(BasePodcast, 'len(url) >= 2 and url[0]=="user"')
def init(self, url, comp, http_method, request):
    name = url[1]
    format = self.choose_format(url[2] if len(url) >= 3 else None)
    feed = self.get_user_feed(name)
    if feed is None:
        raise HTTPNotFound()
    r = RssRenderer()
    r.namespaces = {'itunes': 'http://www.itunes.com/dtds/podcast-1.0.dtd'}
    i = ItunesRenderer(r)
    i.default_namespace = 'itunes'

    with r.rss(version='2.0'):
        with r.channel:
            r << r.title(feed.title)
            r << i.subtitle('%s (%s)' % (feed.description, format.description))
            for v in feed.videos:
                with r.item:
                    r << r.title(v.title)
                    r << r.guid("%s:%s" % (name, v.id), isPermaLink='false')
                    r << r.pubDate(rfc2822(v.published))
                    r << r.enclosure(url=request.relative_url('%s/video.%s?id=%s&fmt=%s' % (self.PREFIX, format.extension, v.id, format.id), to_application=True),
                                     length=10,
                                     type=format.content_type)
                    r << i.duration(v.duration)
                    r << i.subtitle(v.description)
    raise HTTPOk(body=r.root.write_xmlstring(xml_declaration=True, encoding='utf-8', pretty_print=True),
                 content_type='text/xml')

# -------------------------------------------------------------------------------
# Redirect file for download

@presentation.init_for(BasePodcast, 'url and url[0].startswith("video.")')
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
