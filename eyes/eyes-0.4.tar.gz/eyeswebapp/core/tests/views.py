""" view testing """
from django.test import TestCase
from core.models import Monitor, Host
from core.tests.util import mock_nagios_results

class ViewTests(TestCase):
    """ base test setup for the simple views"""

    # TestCase.assertContains(response, text, count=None, status_code=200)
    # Asserts that a Response instance produced the given status_code and that text appears in the content of the response. If count is provided, text must occur exactly count times in the response.
    # 
    # TestCase.assertNotContains(response, text, status_code=200)
    # Asserts that a Response instance produced the given status_code and that text does not appears in the content of the response.
    # 
    # TestCase.assertFormError(response, form, field, errors)
    # Asserts that a field on a form raises the provided list of errors when rendered on the form.
    # form is the name the Form instance was given in the template context.
    # field is the name of the field on the form to check. If field has a value of None, non-field errors (errors you can access via form.non_field_errors()) will be checked.
    # errors is an error string, or a list of error strings, that are expected as a result of form validation.
    # 
    # TestCase.assertTemplateUsed(response, template_name)
    # Asserts that the template with the given name was used in rendering the response.
    # The name is a string such as 'admin/index.html'.
    # 
    # TestCase.assertTemplateNotUsed(response, template_name)
    # Asserts that the template with the given name was not used in rendering the response.
    # TestCase.assertRedirects(response, expected_url, status_code=302, target_status_code=200)

    
    def test_frontpage(self):
        """ testing view results for frontpage of site """
        response = self.client.get('/')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_core_index(self):
        """ testing the index page for /core """
        response = self.client.get('/core/')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_monitor_detail(self):
        """ testing the detail page for monitor #1 """
        response = self.client.get('/core/monitor/1/')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_host_detail(self):
        """ testing the detail page for monitor #1 """
        response = self.client.get('/core/host/1/')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_datastore_detail(self):
        """ testing the detail page for datastore #1 """
        # set up some data to pull...
        mon1 = Monitor.objects.get(id=1)
        self.assertTrue(mon1)
        mock_result_json = mock_nagios_results(type='ping')
        mon1.store_json_results(mock_result_json, debug=False)
        #
        response = self.client.get('/core/datastore/1/')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_datastore_image(self):
        """ testing the image request process for datastore #1 """
        # set up some data to pull...
        mon1 = Monitor.objects.get(id=1)
        self.assertTrue(mon1)
        mock_result_json = mock_nagios_results(type='ping')
        mon1.store_json_results(mock_result_json, debug=False)
        #
        response = self.client.get('/core/datastore/1/png')
        self.failUnlessEqual(response.status_code, 200)
    #
    def test_visual_test_page(self):
        """ working the visual test page"""
        response = self.client.get('/core/visualtest/')
        self.failUnlessEqual(response.status_code, 200)