import unittest
from quant.django.apps.eui.views.testbase import ViewTestCase
from quant.django.apps.eui.views.welcome import WelcomeView

def suite():
    suites = [
        unittest.makeSuite(TestWelcomeView),
    ]
    return unittest.TestSuite(suites)


class TestWelcomeView(ViewTestCase):

    viewClass = WelcomeView
    requiredResponseContent = [
        "Welcome to",
        "What is Quant",
        "Site summary",
        "Using Quant",
    ]

