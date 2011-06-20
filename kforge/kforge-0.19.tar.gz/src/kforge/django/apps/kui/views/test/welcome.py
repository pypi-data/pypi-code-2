import unittest
from kforge.django.apps.kui.views.test.base import ViewTestCase
from kforge.django.apps.kui.views.kui import WelcomeView

def suite():
    suites = [
        unittest.makeSuite(TestWelcomeView),
    ]
    return unittest.TestSuite(suites)


class TestWelcomeView(ViewTestCase):

    viewClass = WelcomeView
    requiredResponseContent = [
        "Welcome to",
        "What is KForge",
        "Site summary",
        "Quick links",
        "Using KForge",
        "KForge Club",

    ]

