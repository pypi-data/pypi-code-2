"""
Views have a redirect() method to easily create redirects:

  >>> getRootFolder()['manfred'] = manfred = Mammoth()

Since the index view redirects to mammoth, we expect to see the URL
point to mammoth:

  >>> from zope.app.wsgi.testlayer import Browser
  >>> browser = Browser()
  >>> browser.handleErrors = False
  >>> browser.open('http://localhost/manfred')
  >>> browser.url
  'http://localhost/manfred/another'

  >>> browser.open('http://localhost/manfred/trustedredirect')
  >>> browser.url
  'http://www.google.com/'

  >>> browser.open('http://localhost/manfred/redirectwithstatus')
  Traceback (most recent call last):
  ...
  HTTPError: HTTP Error 418: Unknown
  >>> browser.url
  'http://localhost/manfred/redirectwithstatus'

"""
import grokcore.view as grok

class Mammoth(grok.Context):
    pass

class Index(grok.View):
    def render(self):
        self.redirect(self.url('another'))

class TrustedRedirect(grok.View):
    def render(self):
        self.redirect('http://www.google.com/ncr', trusted=True)

class RedirectWithStatus(grok.View):
    def render(self):
        self.redirect(self.url(), status=418)

class Another(grok.View):
    def render(self):
        return "Another view"
