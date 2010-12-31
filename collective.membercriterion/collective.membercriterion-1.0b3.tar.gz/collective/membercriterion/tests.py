from unittest import defaultTestLoader

from Products.Five import zcml
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import onsetup

from collective.membercriterion.memberdata import MemberDataCriterion

@onsetup
def setup_product():
    import collective.membercriterion
    zcml.load_config('configure.zcml', collective.membercriterion)

setup_product()
ptc.setupPloneSite(products=['collective.membercriterion'])

class TestCriterion(ptc.PloneTestCase):
    
    def afterSetUp(self):
        self.dummy = self.createDummy()

    def createDummy(self, id='dummy'):
        folder = self.folder
        dummy = MemberDataCriterion(id, 'dummyfield')
        # put dummy in context of portal
        folder._setObject(id, dummy)
        dummy = getattr(folder, id)
        dummy.initializeArchetype()
        return dummy
    
    def test_vocabulary(self):
        vocab = self.dummy.Schema()['property'].Vocabulary(self.dummy)
        self.failUnless('fullname' in vocab.keys())
        self.failUnless('email' in vocab.keys())
        
    def test_query(self):
        self.dummy.Schema()['field'].set(self.dummy, 'Creator')
        self.dummy.setValue('fullname')
        member = self.portal.portal_membership.getAuthenticatedMember()
        member.setProperties(fullname='sample')
        self.assertEquals((('Creator', 'sample'),), self.dummy.getCriteriaItems())
        
    def test_query_invalid_property(self):
        self.dummy.Schema()['field'].set(self.dummy, 'Creator')
        self.dummy.setValue('bogusproperty')
        self.assertEquals((('Creator', None,),), self.dummy.getCriteriaItems())

    def test_anonymous(self):
        self.dummy.Schema()['field'].set(self.dummy, 'Creator')
        self.dummy.setValue('fullname')
        self.logout()
        self.assertEquals((), self.dummy.getCriteriaItems())

    def test_topic_search_criteria(self):
        self.setRoles(['Manager'])
        self.folder.invokeFactory('Topic', id='topic')
        topic = self.folder.topic
        topic.addCriterion('foo', 'MemberDataCriterion')
        self.assertEquals([t.portal_type for t in topic.listSearchCriteria()],
                          ['MemberDataCriterion'])

def test_suite():
    return defaultTestLoader.loadTestsFromName(__name__)
