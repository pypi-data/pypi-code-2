from django.test import TestCase
from panorama.models import *

class AppTestCase(TestCase):
    """
    Populate this class with unit tests for your application
    """

    fixtures = ('panorama',)
    
    urls = 'panorama.test_urls'
    
    def testTemplatetagShowPanoramaLocateInfos(self):
        "Test the show_panorama templatetag: valid panoramainfos"
        from panorama.templatetags.panorama import show_panorama
        panorama = Panorama.objects.get(pk=1) #Get the 'Hall' panorama
        note = PanoramaNote.objects.get(pk=1)
        note2 = PanoramaNote.objects.get(pk=3)
        link = PanoramaExternalLink.objects.get(pk=2)
        context = show_panorama(panorama)
        panoramainfos = context['panoramainfos']
        self.assertEqual(len(panoramainfos),2)
        self.assertTrue(note in panoramainfos)
        self.assertTrue(link in panoramainfos)
        self.assertFalse(note2 in panoramainfos)

    def testPanoramaDetail(self):
        "Test the detail view of a panorama"
        response = self.client.get('/panoramas/1')
        self.assertEqual(response.status_code, 200)
        #Verify jquery.advancedpanorama is loaded
        self.assertContains(response,'panorama/js/jquery.panorama.js')
        #Verify jquery.advancedpanorama is launched for this panorama
        self.assertContains(response,'$("img.advancedpanorama").panorama({')
        #Verify two panoramainfos are shown
        self.assertContains(response,'<area ',2)
        #Verify one panoramainfos is iframe (externallink)
        self.assertContains(response,'class="iframe"',1)
        #Verify one panoramainfos is ajax (note)
        self.assertContains(response,'class="ajax"',1)

    def testPanoramaListing(self):
        "Test the listing view of panoramas"
        response = self.client.get('/panoramas/')
        self.assertEqual(response.status_code, 200)
        #Verify three panoramas are shown
        self.assertContains(response,'<a href="/panoramas/',3)
