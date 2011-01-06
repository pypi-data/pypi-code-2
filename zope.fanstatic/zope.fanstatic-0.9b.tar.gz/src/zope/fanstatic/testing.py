from zope.app.wsgi.testlayer import BrowserLayer
import fanstatic

class ZopeFanstaticBrowserLayer(BrowserLayer):
    """ A zope testlayer with fanstatic Injector. """

    def setup_middleware(self, app):
        return fanstatic.Injector(app)

