# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase


class ZestSocialAddThisViewlet(ViewletBase):

    def show(self):
        try:
            return self.context.show_social_viewlet
        except AttributeError:
            return False
