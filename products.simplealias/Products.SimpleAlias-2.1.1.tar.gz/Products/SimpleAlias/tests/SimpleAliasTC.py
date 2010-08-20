# -*- coding: utf-8 -*-
# $Id: SimpleAliasTC.py 123908 2010-08-20 10:27:22Z glenfant $
# Define a common SimpleAliasTestCase base class for use in all

# Import the base test case classes
import logging, sys
from Products.PloneTestCase import PloneTestCase
from Products.SimpleAlias.config import PROJECTNAME
from Products.Five import fiveconfigure, zcml
from Products.PloneTestCase.layer import PloneSite

PloneTestCase.installProduct(PROJECTNAME)
PloneTestCase.setupPloneSite(products=[PROJECTNAME])


class SimpleAliasTestCase(PloneTestCase.PloneTestCase):

    class layer(PloneSite):

        @classmethod
        def setUp(cls):
            import Products.SimpleAlias
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', Products.SimpleAlias)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass