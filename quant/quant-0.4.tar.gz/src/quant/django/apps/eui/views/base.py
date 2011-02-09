import quant.django.settings.main
from dm.view.base import SessionView

class QuantView(SessionView):

    majorNavigation = []

    def __init__(self, *args, **kwds):
        super(QuantView, self).__init__(*args, **kwds)

    def setMajorNavigationItems(self):
        items = []
        items.append({'title': 'Home', 'url': '/'})
        items.append({'title': 'Symbols', 'url': '/symbols/'})
        items.append({'title': 'Models', 'url': '/models/'})
        items.append({'title': 'Images', 'url': '/images/'})
        items.append({'title': 'Books', 'url': '/books/'})
        items.append({'title': 'Europeans', 'url': '/europeans/'})
        items.append({'title': 'Americans', 'url': '/americans/'})
        items.append({'title': 'Results', 'url': '/results/'})
        self.majorNavigation = items

