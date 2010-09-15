import unittest
import os
import sys
import re

from Products.Five import zcml
from Products.Five import fiveconfigure

from Testing import ZopeTestCase as ztc
from Products.PloneTestCase.layer import onsetup
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.PloneTestCase import portal_owner
from Products.PloneTestCase.PloneTestCase import default_password
from Products.CMFCore.utils import getToolByName

from quintagroup.captcha.core.config import *
from quintagroup.captcha.core import utils
from quintagroup.captcha.core.utils import getWord, decrypt, parseKey, encrypt1

PATCH_WORDS = """heart
glass
blue
false
burn
"""
def testPatch():
    # PATCH dictionary for captcha testing
    class TestData(object):
        words = PATCH_WORDS

    utils.basic_english = TestData()
    utils.CAPTCHAS_COUNT = len(utils.basic_english.words.split())
    # END OF PATCH

@onsetup
def setup_product():
    fiveconfigure.debug_mode = True
    import quintagroup.captcha.core
    zcml.load_config('configure.zcml', quintagroup.captcha.core)
    fiveconfigure.debug_mode = False
    ztc.installPackage('quintagroup.captcha.core')

setup_product()
ptc.setupPloneSite()
