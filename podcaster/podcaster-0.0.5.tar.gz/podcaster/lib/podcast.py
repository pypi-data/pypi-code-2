# -*- coding:utf-8 -*-
import collections
from nagare import editor, validator, presentation

VideoFeed = collections.namedtuple('VideoFeed', 'id,guid,title,published,updated')
UserFeed = collections.namedtuple('UserFeed', 'username,title,videos')
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
