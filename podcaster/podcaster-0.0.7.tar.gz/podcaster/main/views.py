# -*- coding:utf-8 -*-
from nagare import presentation

from comp import Main, PLATFORMS


@presentation.render_for(Main)
def render(self, h, comp, *args):
    h.head.css_url('css/site.css')
    with h.div(id='header'):
        with h.a(href=h.request.relative_url('')):
            h << h.img(src='img/video-icon.png', class_='logo')
        h << h.span(u'Podcaster', class_='app-title')
    with h.div(id='body'):
        h << h.h2("Select platform by clicking on it's icon")
        for p in PLATFORMS:
            h << h.a(h.img(src=p.LOGO)).action(lambda prefix=p.PREFIX: self.select_platform(prefix))
        h << self.podcaster
    with h.div(id='footer'):
        h << u'Powered by : ' << h.a(h.img(src='img/logo_nagare.png', alt='Nagare framework'), href='http://www.nagare.org')
    return h.root
