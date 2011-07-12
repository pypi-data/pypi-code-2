import quant.django.apps.eui.views.welcometest
import quant.django.apps.eui.views.apitest
import unittest

def suite():
    suites = [
        quant.django.apps.eui.views.welcometest.suite(),
        quant.django.apps.eui.views.apitest.suite(),
    ]
    return unittest.TestSuite(suites)

