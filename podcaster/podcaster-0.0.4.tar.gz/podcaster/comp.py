# -*- coding:utf-8 -*-
from nagare import component, editor, validator

from podcaster.lib.video_formats import PREFERED_FORMAT, get_format
from podcaster.lib.youtube import get_video_details, get_user_feed


class Main(object):
    def __init__(self):
        self.menu = (('podcaster', 'Generate podcast', Podcaster), ('downloader', 'Direct download a video', Downloader))
        self.current = ''
        self.content = component.Component(None)
        self.show()

    def show(self, item='podcaster'):
        for id, title, obj in self.menu:
            if id == item:
                self.content.becomes(obj())
                self.current = item
                break


class Podcaster(object):
    def __init__(self):
        self.username = editor.Property('').validate(self.validate_username)
        self.format = editor.Property(PREFERED_FORMAT)
        self.podcast_link = ''

    def validate_username(self, v):
        v = validator.StringValidator(v, strip=True).not_empty().to_string()
        if get_user_feed(v, max_results=1) is None:
            raise ValueError('No channel found for username "%s"' % v)
        return v

    def create_podcast_link(self):
        self.podcast_link = ''
        if not self.username.error:
            self.podcast_link = 'user/%s/%s' % (self.username.value, self.format.value)


class Downloader(object):
    def __init__(self):
#        debug_video = 'hhpxkGB1OyY'
        self.video_id = editor.Property('').validate(self.validate_video_id)
        self.format_id = editor.Property('').validate(lambda v:validator.StringValidator(v).not_empty())
        self.details = None
        self.url = ''

    def validate_video_id(self, v):
        v = validator.StringValidator(v).not_empty().to_string()
        if v != self.video_id.value:
            self.details = get_video_details(self.video_id.value)
            self.format_id.input = self.format_id.value = ''
            self.url = ''
        return v

    def download(self):
        if not any((self.video_id.error, self.format_id.error)) and self.format_id.value:
            format = get_format(self.format_id.value)
            self.url = self.details.urls[self.format_id.value]
            #~ resp = HTTPTemporaryRedirect()
            #~ resp.location = self.url
            #~ resp.content_type = format.content_type
            #~ resp.headers['Content-Disposition'] = 'attachment; filename="%s.%s"' % (self.details.title, format.extension)
            #~ raise resp
