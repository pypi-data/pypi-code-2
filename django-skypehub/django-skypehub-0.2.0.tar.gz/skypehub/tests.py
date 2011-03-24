from django.test import TestCase

from skypehub.decorators import skype_required

class SkypeTest(TestCase):
    def test_get_skype(self):
        decorated = skype_required(lambda req, skype: skype)
        self.assertNotEqual(decorated, None)
