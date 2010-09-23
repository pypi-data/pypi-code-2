from Products.PloneTestCase import ptc
from collective.testcaselayer import ptc as collective_ptc

ptc.setupPloneSite()

class Layer(collective_ptc.BasePTCLayer):
    """Install quintagroup.dropdownmenu"""

    def afterSetUp(self):
        self.addProfile('quintagroup.dropdownmenu:default')

DropDownMenuLayer = Layer([collective_ptc.ptc_layer])
