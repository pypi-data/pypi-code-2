from django.test import TestCase
from django.contrib.auth.models import User
from trawler.models import Target, Campaign

from django.test import Client
from django.core.urlresolvers import reverse

class HitTests(TestCase):
    urls = 'trawler.test_urls'

    def setUp(self):
        self.c = Client()
        self.user = User.objects.create(first_name='foo', last_name='bar',
                                     email='foo@bar.com', password='foo')
        self.c.post('/admin/', {'username': 'foo', 'password': 'bar'})

        self.campaign = Campaign.objects.create(title='test', email_plain='')
        self.target_pk = Target.objects.create(email='pat@example.com',
                                            campaign=self.campaign, pk=123).pk

    def test_image_hit(self):
        self.assertFalse(Target.objects.get(pk=self.target_pk).image_viewed)
        # note: we pass the 2nd arg to satisfy the open-ended regex
        self.c.get(reverse('img_hits', kwargs={'target_id': self.target_pk,
                                               'campaign_id': self.campaign.pk}))
        self.assertTrue(Target.objects.get(pk=self.target_pk).image_viewed)

    def test_link_hit(self):
        self.assertFalse(Target.objects.get(pk=self.target_pk).link_followed)
        # note: we pass the 2nd arg to satisfy the open-ended regex
        self.c.get(reverse('link_hits', kwargs={'target_id': self.target_pk,
                                                'campaign_id': self.campaign.pk}))
        self.assertTrue(Target.objects.get(pk=self.target_pk).link_followed)

class EmailTests(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
