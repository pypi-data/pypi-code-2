# -*- coding:utf-8 -*-
from nagare import presentation

from comp import Main

@presentation.init_for(Main, 'len(url) >= 1')
def init(self, url, comp, http_method, request):
    platform = url[0]
    self.select_platform(platform)
    # Cascade initialize
    self.podcaster.init(url[1:], http_method, request)
