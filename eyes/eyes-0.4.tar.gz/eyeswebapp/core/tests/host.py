"""
This file stores all the tests related to the Host model
"""
from django.test import TestCase
from core.models import Host
from core.tests.util import create_unsaved_minimum_host

class HostTests(TestCase):

    def setUp(self):
        """testing default monitor model data"""
        pass
    
    def test_reverse_url_setup(self):
        """testing reverse url lookup for a Host object"""
        # pylint: disable=E1101
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', 'modeltestdata.json', verbosity=0)
        host = Host.objects.get(pk=1)
        self.assertEquals(host.get_absolute_url(), '/core/host/1/')

    def test_default_data(self):
        """testing default host model data"""
        # pylint: disable=E1101
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        host = create_unsaved_minimum_host()
        host.save()
        self.assertEquals(host.hostname, "localhost")
        self.assertEquals(host.monitor_set.count(), 0)

    def test_default_unicodevalue(self):
        """testing default monitor model data"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        host = create_unsaved_minimum_host()
        host.save()
        self.assertEquals(host.__unicode__(), u'localhost')

