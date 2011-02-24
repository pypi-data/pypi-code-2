import unittest
import provide.django.settings.main as settings
import provide.django.settings.urls.eui as urls

def suite():
    suites = [
        unittest.makeSuite(TestSettings),
        unittest.makeSuite(TestUrls),
    ]
    return unittest.TestSuite(suites)


class TestSettings(unittest.TestCase):

    def test_main(self):
        # stable actual values, check for correct value
        self.failUnlessEqual(settings.TIME_ZONE, 'Europe/Paris')
        self.failUnlessEqual(settings.SECRET_KEY, 'f*(d3d45zetsb3)$&2h5@%lua()yc+kfn4w^dmrf_j1i(6jjkq')
        self.failUnlessEqual(settings.ROOT_URLCONF, 'provide.django.settings.urls.main')

        # unstable actual values, check for any value
        self.failUnless(settings.TEMPLATE_DIRS)

        # abstract settings, check for null value


class TestUrls(unittest.TestCase):

    def test_main(self):
        self.failUnless(urls)
        self.failUnless(urls.urlpatterns)

