from Testing import ZopeTestCase
from Products.PloneTestCase import ptc
from Products.SiteAccess import VirtualHostMonster

from collective.testcaselayer import ptc as tcl_ptc

ptc.setupPloneSite()

class InstallLayer(tcl_ptc.BasePTCLayer):

    def afterSetUp(self):
        ZopeTestCase.installPackage('collective.redirect')
        VirtualHostMonster.manage_addVirtualHostMonster(
            self.app, 'virtual_hosting')
        self.addProfile('collective.redirect:default')
        
install_layer = InstallLayer([ptc.PloneTestCase.layer])
