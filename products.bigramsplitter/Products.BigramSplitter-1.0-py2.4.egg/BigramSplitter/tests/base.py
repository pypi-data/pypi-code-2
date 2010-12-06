# -*- codeing : utf-8 -*-

########################################################################
# test base for bigramspritter.
# Name : base.py  ("base" is translated to "kiso" in Japanese)
# Author : Naotaka Jay Hotta
# Date : Aug/19/2008
# Last modified: Oct/5/2008
# E-mail: hotta@cmscom.jp
#         terada@cmscom.jp
########################################################################

from Testing import ZopeTestCase
from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup

@onsetup
def setup_bigramsplitter():
    fiveconfigure.debug_mode = True
    from Products import BigramSplitter
    zcml.load_config('configure.zcml', BigramSplitter)
    fiveconfigure.debug_mode = False
    
    ZopeTestCase.installPackage('BigramSplitter')

setup_bigramsplitter()

PRODUCTS = []
PloneTestCase.setupPloneSite(products=PRODUCTS)


class BigramSplitterTestCase(PloneTestCase.PloneTestCase):
    class Session(dict):
        def set(self, key, value):
            self[key] = value
    
    def _setup(self):
        PloneTestCase.PloneTestCase._setup(self)
        self.app.REQUEST['SESSION'] = self.Session()
        
        # なぜ、initialize　が Quicinstall 時に、GenericSetupよりも前に動かないのか?
        # Word Splitter の登録も、GenericSetup で可能なのか??
        from Products.BigramSplitter import BigramSplitter
