import unittest
import datetime
import traceback
import sys
from campaign_monitor_api import CampaignMonitorApi


def error_print():
    print "|||==========================="
    print sys.exc_info()[0]
    print "|||--------------------------"
    print traceback.print_exc()
    print "|||--------------------------"


class CampaignMonitorTestCaseError(Exception):
    pass


class CampaignMonitorTestCase(unittest.TestCase):
    '''
        Basic test coverage.  Requires an active Campaign Monitor account - so make sure you setup and use your TEST account details.
        Use runtests.py to set these
    '''
    
    cm_api_key = None # update to your API key in runtests.py
    cm_client_id = None # update with your TEST client ID in runtests.py
    cm_list_id = None # update with your TEST list ID in runtests.py
    cm_testing_email_address = None # update with email address in runtests.py
    cm_test_add = False # should we test the ADD method? set in runtests.py
    cm_custom_fields = {} # setup test values for the custom fields for your test list in runtests.py.  Note: these tests require these fields to be setup in your Campaign Monitor TEST list
    debug = False
    
    def setUp(self):
        
        if not self.cm_api_key :
            raise CampaignMonitorTestCaseError('cm_api_key not defined')
        
        if not self.cm_client_id :
            raise CampaignMonitorTestCaseError('cm_client_id not defined')
        
        if not self.cm_list_id :
            raise CampaignMonitorTestCaseError('cm_list_id not defined')
        
        if not self.cm_testing_email_address :
            raise CampaignMonitorTestCaseError('cm_testing_email_address not defined')


    def test_init(self):
        '''
            Confirms that setting the core properties works as expected.
        '''
        
        cm_api = CampaignMonitorApi(self.cm_api_key, self.cm_client_id)
        
        # make sure that setting the API and ClientID properties work correctly
        self.assertEquals(cm_api.api_key, self.cm_api_key)
        self.assertEquals(cm_api.client_id, self.cm_client_id)


    def test_client_namespace(self):
        '''
            Confirms Client.xxxx functions work correctly.
        '''
        
        cm_api = CampaignMonitorApi(self.cm_api_key, self.cm_client_id)
        
        # grab the current lists using the inline client_id
        lists = cm_api.client_get_lists()
        self.assert_(True)
        
        # grab the current lists using a passed-in client_id
        lists = cm_api.client_get_lists( client_id=self.cm_client_id )
        self.assert_(True)
        
        # grab the supression list using the in-object client_id
        lists = cm_api.client_get_supression_list()
        self.assert_(True)
        
        # grab the supression list using a passed-in client_id
        lists = cm_api.client_get_supression_list( client_id=self.cm_client_id )
        self.assert_(True)


    def test_subscriber_namespace(self):
        '''
            Confirms Subscriber(s).xxxx functions work correctly.
        '''
        
        cm_api = CampaignMonitorApi(self.cm_api_key, self.cm_client_id)
        
        if self.cm_test_add:
            # try subscribing, without custom fields
            ok = cm_api.subscriber_add(self.cm_list_id, self.cm_testing_email_address, "Test Person")
            self.assertEquals(ok, True)
        else:
            # ensure the user is subscribed at least once.  WITHOUT custom fields
            # note that this calls "subscriber_add_and_resubscribe" not "subscriber_add"
            ok = cm_api.subscriber_add_and_resubscribe(self.cm_list_id, self.cm_testing_email_address, "Test Person" )
            self.assertEquals(ok, True)
        
        # check to see that the email is now subscribed
        # the user should be subscribed
        res = cm_api.subscribers_get_is_subscribed(self.cm_list_id, self.cm_testing_email_address)
        self.assertEquals(res, True) 
        
        # remove the user
        ok = cm_api.subscriber_unsubscribe(self.cm_list_id, self.cm_testing_email_address)
        self.assertEquals(ok, True)
        
        # check to see that the email is subscribed
        # the user should NOT be subscribed
        res = cm_api.subscribers_get_is_subscribed(self.cm_list_id, self.cm_testing_email_address)
        self.assertEquals(res, False) 
        
        # the api raises an except if we add someone who has been removed
        self.assertRaises( CampaignMonitorApi.CampaignMonitorApiException , cm_api.subscriber_add , self.cm_list_id, self.cm_testing_email_address, "Test Person")
        
        # check to see that the email is subscribed
        # the user should NOT be subscribed
        res = cm_api.subscribers_get_is_subscribed(self.cm_list_id, self.cm_testing_email_address)
        self.assertEquals(res, False) 
        
        # use the correct method to add this user
        ok = cm_api.subscriber_add_and_resubscribe(self.cm_list_id, self.cm_testing_email_address, "Test Person")
        self.assertEquals(ok, True)
        
        # check to see that the email is subscribed
        # the user should be subscribed
        res = cm_api.subscribers_get_is_subscribed(self.cm_list_id, self.cm_testing_email_address)
        self.assertEquals(res, True) # should now be re-added
        
        if self.cm_test_custom_fields:
            # try adding this user with custom fields
            ok = cm_api.subscriber_add_and_resubscribe(self.cm_list_id, self.cm_testing_email_address, "Test Person", custom_fields=self.cm_custom_fields)
            self.assertEquals(ok, True)
        
            # check to see that the email is subscribed
            # the user should be subscribed
            res = cm_api.subscribers_get_is_subscribed(self.cm_list_id, self.cm_testing_email_address)
            self.assertEquals(res, True) # should now be re-added
        
            # check the custom fields data
            res = cm_api.subscribers_get_single_subscriber(self.cm_list_id, self.cm_testing_email_address)
            cf_seen = True
            for item in self.cm_custom_fields.keys():
                if item not in res['Subscribers.GetSingleSubscriber'][0]['CustomFields']:
                    cf_seen = False
            self.assertEquals(cf_seen, True) # we've seen all the correct items.  i guess we could have raised an error on missing instead.
            
        # test that we can check for active subscribers ; these will all raise errors if we fail
        res = cm_api.subscribers_get_active(self.cm_list_id )
        res = cm_api.subscribers_get_bounced(self.cm_list_id )
        res = cm_api.subscribers_get_unsubscribed(self.cm_list_id )


    def test_list_namespace(self):
        '''
            Confirms List.xxxx functions work correctly.
        '''
        
        cm_api = CampaignMonitorApi(self.cm_api_key, self.cm_client_id)
        
        # Update the list's details
        res = cm_api.list_update(
            self.cm_list_id,
            "Test list", 
            "www.example.com/unsubscribe", 
            True, 
            "www.example.com/confirmation"
        )
        self.assert_(res)

        # Check that the returned details are correct
        detail = cm_api.list_get_detail(self.cm_list_id)

        self.assertEquals(self.cm_list_id, detail.get("ListID"))
        self.assertEquals("Test list", detail.get("Title"))
        self.assertEquals(
            "www.example.com/unsubscribe", 
            detail.get("UnsubscribePage")
        )
        self.assertEquals("true", detail.get("ConfirmOptIn"))
        self.assertEquals(
            "www.example.com/confirmation",
            detail.get("ConfirmationSuccessPage")
        )


    def test_bad_data(self):
        '''
            Confirms that the class fails correctly if bad data is provided.
        '''
        
        cm_api = CampaignMonitorApi(self.cm_api_key, self.cm_client_id)
        
        # test two methods with invalid list ID
        self.assertRaises(CampaignMonitorApi.CampaignMonitorApiException, cm_api.add_and_resubscribe, 0, self.cm_testing_email_address, "Test Person")
        self.assertRaises(CampaignMonitorApi.CampaignMonitorApiException, cm_api.add, 0, self.cm_testing_email_address, "Test Person")
