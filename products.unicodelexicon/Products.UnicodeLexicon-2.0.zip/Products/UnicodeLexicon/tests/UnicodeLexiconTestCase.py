
from Products.CMFTestCase import CMFTestCase

CMFTestCase.installProduct('UnicodeLexicon', quiet=True)
CMFTestCase.setupCMFSite(extension_profiles=('Products.UnicodeLexicon:default',))

default_user = CMFTestCase.default_user
default_password = CMFTestCase.default_password


class UnicodeLexiconTestCase(CMFTestCase.CMFTestCase):
    pass

class FunctionalTestCase(CMFTestCase.Functional, UnicodeLexiconTestCase):
    pass

