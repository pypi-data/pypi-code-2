from plone.app.blob.tests import db # needs to be imported first to set up ZODB
db  # make pyflakes happy...

from Products.Five.testbrowser import Browser
from Products.PloneTestCase import PloneTestCase as ptc
from Products.RichImage.tests.layer import RichImageLayer
from Products.RichImage.tests.utils import getFile
from Testing import ZopeTestCase as ztc

profiles = ['Products.RichImage:default']
HAS_LINGUA = True
try:
    import Products.LinguaPlone
    ztc.installProduct('LinguaPlone')
    profiles[0:0] = ['Products.LinguaPlone:LinguaPlone']
except ImportError:
    HAS_LINGUA = False

ztc.installProduct('RichImage')

ptc.setupPloneSite(extension_profiles=tuple(profiles))


class RichImageTestCase(ptc.PloneTestCase):
    """ base class for integration tests """

    layer = RichImageLayer

    test_image = getFile('image.png').read()
    test_image_small = getFile('image_small.png').read()
    test_image_jpg = getFile('image.jpg').read()


class RichImageFunctionalTestCase(ptc.FunctionalTestCase):
    """ base class for functional tests """

    layer = RichImageLayer

    test_image = getFile('image.png')
    test_image_small = getFile('image_small.png')

    def getBrowser(self, loggedIn=True):
        """ instantiate and return a testbrowser for convenience """
        browser = Browser()
        if loggedIn:
            credentials = ptc.default_user, ptc.default_password
            browser.addHeader('Authorization', 'Basic %s:%s' % credentials)
        return browser

