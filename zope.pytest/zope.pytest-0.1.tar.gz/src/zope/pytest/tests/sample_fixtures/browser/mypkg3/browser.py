from zope.publisher.browser import BrowserPage

class SampleAppView(BrowserPage):

    def __call__(self):
        self.request.response.setHeader('Content-Type', 'text/plain')
        return u'Hello from SampleAppView!'
