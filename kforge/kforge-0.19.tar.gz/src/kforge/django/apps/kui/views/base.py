import kforge.django.settings.main
from dm.view.base import SessionView
import kforge.url

class KforgeView(SessionView):

    majorNavigation = [
        {'title': 'Home',      'url': '/'},
        {'title': 'Your Page', 'url': '/person/home/'},
        {'title': 'People',    'url': '/person/'},
        {'title': 'Projects',  'url': '/project/'},
    ]

    def setContext(self, **kwds):
        super(KforgeView, self).setContext(**kwds)
        url_scheme = kforge.url.UrlScheme()
        self.context.update({
            'kforge_media_url' : url_scheme.url_for('media'),
        })  

