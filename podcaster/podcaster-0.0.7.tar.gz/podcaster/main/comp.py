# -*- coding:utf-8 -*-
from nagare import component
from podcaster.platforms.youtube.comp import YTPodcast
from podcaster.platforms.dailymotion.comp import DMPodcast

PLATFORMS = (YTPodcast, DMPodcast)

class Main(object):
    def __init__(self):
        self.podcaster = component.Component(None)
        self.select_platform(PLATFORMS[0].PREFIX)

    def select_platform(self, prefix):
        for p in PLATFORMS:
            if p.PREFIX == prefix:
                self.podcaster.becomes(p())
