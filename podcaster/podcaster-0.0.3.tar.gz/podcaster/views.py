# -*- coding:utf-8 -*-
from nagare import presentation

from podcaster.comp import Main, Downloader, Podcaster
from podcaster.lib.video_formats import get_format, SUPPORTED_FORMATS


@presentation.render_for(Main)
def render(self, h, comp, *args):
    h.head.css_url('css/site.css')
    with h.div(id='header'):
        with h.a(href=h.request.relative_url('')):
            h << h.img(src='img/video-icon.png', class_='logo')
        h << h.span(u'Podcaster', class_='app-title')
    with h.div(id='menu'):
        with h.ul:
            for id, title, obj in self.menu:
                if id == self.current:
                    h << h.li(title, class_='selected')
                else:
                    h << h.li(h.a(title).action(lambda id=id: self.show(id)))
    with h.div(id='body'):
        h << self.content
    with h.div(id='footer'):
        h << u'Powered by : ' << h.a(h.img(src='img/logo_nagare.png', alt='Nagare framework'), href='http://www.nagare.org')
    return h.root


@presentation.render_for(Downloader)
def render(self, h, comp, *args):
    with h.form:
        h << h.h2('Choose your video')
        h << h.div('Video ID')
        h << h.input(value=self.video_id()).action(self.video_id).error(self.video_id.error) << ' '
        if self.details:
            h << h.div('Choose desired format')
            with h.select.action(self.format_id):
                for id in self.details.urls:
                    fmt = get_format(id)
                    h << h.option(fmt.description, value=fmt.id)
        h << h.div(h.input(type='submit').action(self.download), class_='submit')
    if self.url:
        h << h.h2('Here is your video')
        h << h.a(self.url, href=self.url)
    return h.root


@presentation.render_for(Podcaster)
def render(self, h, comp, *args):
    with h.form:
        h << h.h2('Generate your podcast link')
        h << h.div('YouTube Username')
        h << h.input(value=self.user_name()).action(self.user_name).error(self.user_name.error) << ' '
        h << h.div('Choose desired format')
        with h.select.action(self.format):
            h << [h.option(f.description, value=f.id).selected(self.format()) for f in SUPPORTED_FORMATS] << ' '
        h << h.div(h.input(type='submit', value='Get my link').action(self.create_podcast_link), class_='submit')
    if self.podcast_link:
        h << h.h2('Here is your link !')
        abs_url = h.request.relative_url(self.podcast_link)
        h << h.div(h.a(abs_url, href=abs_url), class_='podcast-link')
    return h.root
