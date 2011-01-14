# This script runs the Campaign Monitor API unit tests using your specific API details
from campaign_monitor_api_tests import CampaignMonitorTestCase
import unittest

# Setup your the API details for your TEST client in Campaign Monitor.
# Details on how to find your API key and other details in Campaign Monitor can be found at:
# http://www.campaignmonitor.com/api/required/
CampaignMonitorTestCase.cm_api_key = "xxx" # update to your API key
CampaignMonitorTestCase.cm_client_id = "xxx" # update with your TEST client ID
CampaignMonitorTestCase.cm_list_id = "xxx" # update with your TEST list ID
# By design the Campaign Monitor "Subscriber.Add" method will throw an exception if you attempt to add a user 
# that has already in the Subscriber list - even if they have been unsubscribed or deleted.  As such, for each
# test run that includes "Subscriber.Add" you need to either:
# a) clear the suppression list for the client via the Campaign Monitor administration interface
# b) use a brand new email address for each test
# For these reasons, the test class allow you to disable this single method's tests by setting the cm_test_add 
# property to False, in case you want to run all other tests during development without triggering this behaviour
CampaignMonitorTestCase.cm_test_add = False # debug add function
CampaignMonitorTestCase.cm_testing_email_address = "xxx" # update with the (unique) TEST email address you want to add to the list
CampaignMonitorTestCase.cm_test_custom_fields = False # set to true if you want to test custom fields - REQUIRES you set cm_custom_fields to match your list
# CampaignMonitorTestCase.cm_custom_fields = { "field1":"value1", "field2":"value2" } # REQUIRED when cm_test_custom_fields = True
# NOTE: Campaign Monitor custom fields are case sensitive - check the Custom Fields screen for your list to confirm the case
CampaignMonitorTestCase.debug = True # debug testing

# run tests
suite = unittest.TestLoader().loadTestsFromTestCase(CampaignMonitorTestCase)
unittest.TextTestRunner(verbosity=2).run(suite)
