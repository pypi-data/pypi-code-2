"""
This file stores all the tests related to the REST API for monitors
"""
from django.test import TestCase
from core.models import Monitor
from core.tests.util import mock_nagios_results
from eyeswebapp.util.monitor import ArgSet
import simplejson

class MonitorTests(TestCase):
    """ test cases for the Monitor API """

    # def setUp(self):
    #     """testing default monitor model data"""
    #     pass
    #
    expected_keys = ['lastupdate', 'plugin_name', 'name', 'json_argset', 'nextupdate', 'id']

    def test_docs(self):
        """ invoking /api/ to get basic docs... """
        response = self.client.get('/api')
        self.failUnlessEqual(response.status_code, 301)
        response = self.client.get('/api/')
        self.failUnlessEqual(response.status_code, 200)
    
    def test_monitor_list_api(self):
        """ invoking /api/monitor/ to get a list of pending monitors... """
        response = self.client.get('/api/monitor')
        self.failUnlessEqual(response.status_code, 301)
        response = self.client.get('/api/monitor/')
        self.failUnlessEqual(response.status_code, 200)
        
        objresult = simplejson.loads(response.content)
        self.assertEquals(type(objresult), type([])) # is a list
        self.assertTrue(len(objresult) > 0)
    #
    def test_monitor_detail_api(self):
        """ /api/monitor/ piston.resource.<piston.resource.Resource object at 0x101bd1550> """
        response = self.client.get('/api/monitor/1')
        self.failUnlessEqual(response.status_code, 301)
        response = self.client.get('/api/monitor/1/')
        self.failUnlessEqual(response.status_code, 200)

        objresult = simplejson.loads(response.content)
        self.assertEquals(type(objresult), type({})) # is a dictionary
        for element in self.expected_keys:
            self.assertTrue(element in objresult.keys(), "%s not in returned keys" % element)

    def test_monitor_missing_api(self):
        response = self.client.get('/api/monitor/9999/')
        self.failUnlessEqual(response.status_code, 404)

    def test_monitor_missing_store_api(self):
        response = self.client.get('/api/monitor/9999/store/')
        # expect a refusal on "GET"
        self.failUnlessEqual(response.status_code, 405)

    def test_monitor_store_refusal(self):
        """ tests expect a 405 (not allowed) from a GET response to an existing /monitor/[ID]/store/ call """
        response = self.client.get('/api/monitor/1/store/')
        self.failUnlessEqual(response.status_code, 405)
    
    def test_quick_check_mock_data(self):
        """testing that mock data is valid"""
        from util.monitor import validate_poller_results
        mock_nagios_json_data = mock_nagios_results()
        validated = validate_poller_results(mock_nagios_json_data)
        self.assertTrue(validated)
    
    def test_post_ping_data(self):
        """ tests posting a PING monitor result as JSON data """
        mock_nagios_json_data = mock_nagios_results()
        response = self.client.post('/api/monitor/1/store/', content_type='application/json', data = mock_nagios_json_data )
        self.failUnlessEqual(response.status_code, 201)

    def test_post_ping_data_bad_monitor(self):
        """ tests failure posting a monitor result as JSON data (non-exist monitor)"""
        mock_nagios_json_data = mock_nagios_results()
        response = self.client.post('/api/monitor/9999/store/', content_type='application/json', data = mock_nagios_json_data )
        self.failUnlessEqual(response.status_code, 404)
    
    def test_flawed_data_post(self):
        """ testing posting of flawed result dictionary"""
        bad_mock_data = {'command': '/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%', } 
        response = self.client.post('/api/monitor/1/store/', content_type='application/json', data = bad_mock_data )
        self.failUnlessEqual(response.status_code, 400)
    
    def test_non_json_post_to_store_monitor_result(self):
        """ testing flawed posting mechanism
        should fail with Bad Request"""
        response = self.client.post('/api/monitor/1/store/', {'name': 'fred', 'passwd': 'secret'})
        self.failUnlessEqual(response.status_code, 400)
        