import quant.django.settings.main
from dm.view.base import SessionView

class QuantView(SessionView):

    majorNavigation = []

    def __init__(self, *args, **kwds):
        super(QuantView, self).__init__(*args, **kwds)

    def setMajorNavigationItems(self):
        items = []
        items.append({'title': 'Home',      'url': '/'})
        items.append({'title': 'Markets', 'url': '/markets/'})
        #items.append({'title': 'Pricers', 'url': '/pricers/'})
        #items.append({'title': 'Calculator', 'url': '/calculator/'})
        items.append({'title': 'Europeans', 'url': '/europeanOptions/'})
        items.append({'title': 'Americans', 'url': '/americanOptions/'})
        #items.append({'title': 'Asians', 'url': '/asianOptions/'})
        #items.append({'title': 'Exotics', 'url': '/exoticOptions/'})
        items.append({'title': 'Books', 'url': '/books/'})
        self.majorNavigation = items

