from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from Products.salesforcebaseconnector.tests.layer import SalesforcePloneLayer
from collective.salesforce.rsvp import config

ztc.installProduct('salesforcebaseconnector')

class SFRSVPTestCase(ptc.PloneTestCase):
    
    layer = SalesforcePloneLayer
    
    _toCleanUp = []
    
    def _createCampaignForCleanup(self):
        # create a Campaign and append to the list of campaigns for cleanup
        campaign = dict(type='Campaign',
            Name='Fake Plone Test Case Campaign',
            IsActive=True,
        )
        res = self.sbc.create(campaign)
        sfCampaignId = res[0]['id']
        self._toCleanUp.append(sfCampaignId)
        
        # return campaign id for use by caller
        return sfCampaignId
    
    def _configureRSVPableObject(self, obj):
        # encapsulate reasonable setup of a provided
        # object that has already been said to provide
        # the ISalesforceRSVPable interface
        
        sfCampaignId = self._createCampaignForCleanup()
        
        # set rsvpable schema fields
        obj.getField('sfObjectId').set(obj, sfCampaignId)
        obj.getField('sfObjectSignupType').set(obj, 'Campaign')
        
        return sfCampaignId
    
    def _setMaxCapacityValue(self, sfCampaignId, maxCapFName, num):
        # central setting of the max capacity value
        updateData = dict(Id=sfCampaignId, 
                          type='Campaign',)
        updateData[maxCapFName] = num
        
        self.sbc.update(updateData)
    
    def _setWaitlistableStatus(self, sfCampaignId, statusFName, status):
        # central setting of the waitlistable status value value
        updateData = dict(Id=sfCampaignId, 
                          type='Campaign',)
        updateData[statusFName] = status
        
        self.sbc.update(updateData)
    
    def afterSetUp(self):
        self._toCleanUp = []
    
    def beforeTearDown(self):
        if len(self._toCleanUp):
            self.sbc.delete(self._toCleanUp)

@onsetup
def load_zcml():
    fiveconfigure.debug_mode = True
    import collective.salesforce.rsvp
    zcml.load_config('configure.zcml',
                     collective.salesforce.rsvp)
    fiveconfigure.debug_mode = False

load_zcml()
ptc.setupPloneSite(products=[config.PROJECTNAME,])

class SFRSVPFunctionalTestCase(ptc.FunctionalTestCase):
    """Test case class used for functional (doc-)tests
    """