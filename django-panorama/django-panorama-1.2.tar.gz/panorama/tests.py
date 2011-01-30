"Tests for django-panorama"

from django.test import TestCase
from panorama.models import Panorama, Note, ExternalLink

class AppTestCase(TestCase):
    """
    Populate this class with unit tests for your application
    """

    fixtures = ('panorama',)
    
    urls = 'panorama.test_urls'
    
    def test_templatetag_show_panorama(self):
        "Test the show_panorama templatetag: valid panoramainfos"
        from panorama.templatetags.panoramas import show_panorama
        panorama = Panorama.objects.get(pk=1) #Get the 'Hall' panorama
        note = Note.objects.get(pk=1)
        note2 = Note.objects.get(pk=3)
        link = ExternalLink.objects.get(pk=2)
        request = {}
        context = show_panorama(request, panorama)
        panoramainfos = context['panoramainfos']
        self.assertEqual(len(panoramainfos), 2)
        self.assertTrue(note in panoramainfos)
        self.assertTrue(link in panoramainfos)
        self.assertFalse(note2 in panoramainfos)

    def test_panorama_detail(self):
        "Test the detail view of a panorama"
        response = self.client.get('/panoramas/1')
        self.assertEqual(response.status_code, 200)
        #Verify jquery.advancedpanorama is loaded
        self.assertContains(response, 'panorama/js/jquery.panorama.js')
        #Verify jquery.advancedpanorama is launched for this panorama
        self.assertContains(response, '$("img.advancedpanorama").panorama({')
        #Verify two panoramainfos are shown
        self.assertContains(response, '<area ', 2)
        #Verify one panoramainfos is iframe (externallink)
        self.assertContains(response, 'class="iframe"', 1)
        #Verify one panoramainfos is ajax (note)
        self.assertContains(response, 'class="ajax"', 1)

    def test_panorama_listing(self):
        "Test the listing view of panoramas"
        response = self.client.get('/panoramas/')
        self.assertEqual(response.status_code, 200)
        #Verify three panoramas are shown
        self.assertContains(response, '<a href="/panoramas/', 3)
