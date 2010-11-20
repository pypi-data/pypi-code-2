"""
This file stores all the tests related to the Monitor model
"""
from django.test import TestCase
from core.models import Monitor
from core.models import Datastore
from core.models import Host
from eyeswebapp.util.monitor import ArgSet
import datetime
import simplejson
from core.tests.util import create_unsaved_minimum_monitor
from core.tests.util import create_unsaved_minimum_host
from core.tests.util import mock_nagios_results
from core.tests.util import clear_all_rrd_files
from pyrrd.rrd import RRD

class MonitorTests(TestCase):
    """ test cases for the Monitor model object"""

    def setUp(self):
        """testing default monitor model data"""
        clear_all_rrd_files()
    
    def test_reverse_url_setup(self):
        """testing reverse url lookup for a model object"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', 'modeltestdata.json', verbosity=0)
        xmon = Monitor.objects.get(pk=1)
        self.assertEquals(xmon.get_absolute_url(), '/core/monitor/1/')

    def test_host_monitor_linkages(self):
        # pylint: disable=E1101
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        management.call_command('loaddata', 'modeltestdata.json', verbosity=0)
        xmon = Monitor.objects.get(pk=1)
        self.assertEquals(xmon.get_absolute_url(), '/core/monitor/1/')
        newhost = create_unsaved_minimum_host()
        newhost.save()
        xmon.host = newhost
        xmon.save()
        self.assertEquals(xmon.__unicode__(), u'Monitor example_ping_monitor (check_ping) against localhost')
        self.assertEquals(xmon.host.hostname, "localhost")
        self.assertEquals(newhost.monitor_set.count(), 1)

    def test_default_data(self):
        """testing default monitor model data"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.save()
        self.assertEquals(newmonitor.lastupdate, None)

    def test_default_passive_attribute(self):
        """testing default monitor model data - passive attribute"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.save()
        self.assertEquals(newmonitor.passive, False)

    def test_default_unicodevalue(self):
        """testing default monitor model data"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.save()
        self.assertEquals(newmonitor.__unicode__(), u'Monitor newmonitor (check_ping) against None')

    def test_pending_query(self):
        """testing the manager's pending monitors method to get monitors with nextupdate set to NULL"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        oldmonitor = create_unsaved_minimum_monitor()
        oldmonitor.name = "foo"
        oldmonitor.nextupdate = None
        oldmonitor.save()
        pending_query_set = Monitor.objects.pending_update()
        self.assertEquals(len(pending_query_set), 2)

    def test_pending_query_with_passive(self):
        """testing the manager's pending monitors method to get monitors with nextupdate set to NULL"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        oldmonitor = create_unsaved_minimum_monitor()
        oldmonitor.name = "foo"
        oldmonitor.nextupdate = None
        oldmonitor.save()
        mon2 = create_unsaved_minimum_monitor()
        mon2.name = "passivetest"
        mon2.nextupdate = None
        mon2.passive = True
        mon2.save()
        pending_query_set = Monitor.objects.pending_update()
        self.assertEquals(len(pending_query_set), 2)
        
    def test_pending_query2(self):
        """testing the manager's pending monitors method"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        oldmonitor = create_unsaved_minimum_monitor()
        oldmonitor.name = "old"
        oldmonitor.poll_frequency = 10

        futuremonitor = create_unsaved_minimum_monitor()
        futuremonitor.name = "future"
        futuremonitor.poll_frequency = 10

        now = datetime.datetime.now()
        yesterday = now-datetime.timedelta(days=1)
        tomorrow = now+datetime.timedelta(days=1)
        oldmonitor.lastupdate = yesterday
        futuremonitor.lastupdate = tomorrow
        oldmonitor.nextupdate = yesterday
        futuremonitor.nextupdate = tomorrow
        oldmonitor.save()
        futuremonitor.save()
        # get the details of the test - pending monitors
        pending_query_set = Monitor.objects.pending_update()
        self.assertEquals(len(pending_query_set), 2)
        # update the pending monitors
        for mon in pending_query_set:
            mon.state = 1
            mon.save()
        # check again - pending monitors
        pending_query_set = Monitor.objects.pending_update()
        # for mon in pending_query_set:
        #     print mon.name, mon.nextupdate
        self.assertEquals(len(pending_query_set), 0)

    def test_pending_query_with_passive_and_update(self):
        """testing the manager's pending monitors method"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        oldmonitor = create_unsaved_minimum_monitor()
        oldmonitor.name = "old"
        oldmonitor.poll_frequency = 10

        futuremonitor = create_unsaved_minimum_monitor()
        futuremonitor.name = "future"
        futuremonitor.poll_frequency = 10

        passivemonitor = create_unsaved_minimum_monitor()
        passivemonitor.name = "passive"
        passivemonitor.poll_frequency = 10
        passivemonitor.passive = True

        now = datetime.datetime.now()
        yesterday = now-datetime.timedelta(days=1)
        tomorrow = now+datetime.timedelta(days=1)
        oldmonitor.lastupdate = yesterday
        futuremonitor.lastupdate = tomorrow
        passivemonitor.lastupdate = yesterday
        oldmonitor.nextupdate = yesterday
        futuremonitor.nextupdate = tomorrow
        oldmonitor.save()
        futuremonitor.save()
        passivemonitor.save()
        # get the details of the test - pending monitors
        pending_query_set = Monitor.objects.pending_update()
        self.assertEquals(len(pending_query_set), 2)
        # update the pending monitors
        for mon in pending_query_set:
            mon.state = 1
            mon.save()
        # check again - pending monitors
        pending_query_set = Monitor.objects.pending_update()
        # for mon in pending_query_set:
        #     print mon.name, mon.nextupdate
        self.assertEquals(len(pending_query_set), 0)

    def test_passive_update(self):
        """testing the manager's pending monitors method"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        passivemonitor = create_unsaved_minimum_monitor()
        passivemonitor.name = "passive"
        passivemonitor.poll_frequency = 10
        passivemonitor.passive = True

        now = datetime.datetime.now()
        yesterday = now-datetime.timedelta(days=1)
        tomorrow = now+datetime.timedelta(days=1)
        passivemonitor.lastupdate = yesterday
        passivemonitor.save()

        passive_mon_list = Monitor.objects.filter(passive__exact=True)
        self.assertEquals(len(passive_mon_list), 1)
        for mon in passive_mon_list:
            mon.state = 1
            mon.save()
        the_passive_mon = passive_mon_list[0]
        self.assertTrue(the_passive_mon.lastupdate > yesterday)
        self.assertTrue(the_passive_mon.nextupdate is None)

    def test_setting_state1(self):
        """testing setting state & default value"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "testsettingstate"
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 0)
        self.assertEquals(newmonitor.state, 0)
        self.assertEquals(newmonitor.state_display, u'ok')

    def test_setting_state2(self):
        """testing setting state & default value"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "testsettingstate"
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 0)
        self.assertEquals(newmonitor.state, 0)
        self.assertEquals(newmonitor.state_display, u'ok')
        point_in_time = datetime.datetime.now()
        newmonitor.state = 1
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 1)
        self.assertEquals(newmonitor.state, 1)
        self.assertEquals(newmonitor.state_display, u'warning')
        self.assertTrue(newmonitor.lastupdate > point_in_time)
        self.assertTrue(newmonitor.nextupdate > point_in_time)
    
    def test_setting_state3(self):
        """testing setting state & display value"""
        clear_all_rrd_files()
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "testsettingstate"
        newmonitor.state = 1
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 1)
        self.assertEquals(newmonitor.state, 1)
        self.assertEquals(newmonitor.state_display, u'warning')
        newmonitor.state = 2
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 2)
        self.assertEquals(newmonitor.state, 2)
        self.assertEquals(newmonitor.state_display, u'error')
        newmonitor.state = 3
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 3)
        self.assertEquals(newmonitor.state, 3)
        self.assertEquals(newmonitor.state_display, u'unknown')
        newmonitor.state = 4
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 3)
        self.assertEquals(newmonitor.state, 3)
        self.assertEquals(newmonitor.state_display, u'unknown')
        newmonitor.state = -1
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 3)
        self.assertEquals(newmonitor.state, 3)
        self.assertEquals(newmonitor.state_display, u'unknown')
        newmonitor.state = None
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 3)
        self.assertEquals(newmonitor.state, 3)
        self.assertEquals(newmonitor.state_display, u'unknown')
        newmonitor.state = 0
        newmonitor.save()
        self.assertEquals(newmonitor.latest_state, 0)
        self.assertEquals(newmonitor.state, 0)
        self.assertEquals(newmonitor.state_display, u'ok')
    #
    def test_default_argset(self):
        """testing default monitor model json data for argset"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.save()
        self.assertEquals(newmonitor.arg_set, None)
    #
    def test_setting_argset_none(self):
        """testing setting an argset to None"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        xargset = ArgSet()
        xargset.add_argument('--help')
        newmonitor.arg_set = xargset
        newmonitor.save()
        newmonitor.arg_set = None
        newmonitor.save()
        self.assertEquals(newmonitor.json_argset, '')
    #
    def test_setting_argset_none2(self):
        """testing setting an argset to None"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.json_argset = None
        self.assertEquals(newmonitor.arg_set, None)
    #
    def test_setting_argset(self):
        """testing setting an argset into a model"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.save()
        xargset = ArgSet()
        xargset.add_argument('--help')
        newmonitor.arg_set = xargset
        zed1 = newmonitor.arg_set.json()
        zed2 = xargset.json()
        self.assertEquals(zed1, zed2)
        argjson = xargset.json()
        self.assertEquals(newmonitor.json_argset, argjson)
    #
    def test_setting_argset2(self):
        """testing setting an argset into a model, make sure we can get the json back out again"""
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "testsettingargset"
        xargset = ArgSet()
        xargset.add_argument('--help')
        newmonitor.arg_set = xargset
        newmonitor.save()        
        mon_list = Monitor.objects.filter(name='testsettingargset')
        self.assertEquals(len(mon_list), 1)
        that_monitor = mon_list[0]
        self.assertEquals(xargset.json(), that_monitor.json_argset)
    #
    def test_verify_mock(self):
        """ verifying mock objects return something appropriate """
        self.assertTrue(mock_nagios_results())
        self.assertTrue(mock_nagios_results(type='http'))
        pingdict = simplejson.loads(mock_nagios_results(type='ping'))
        httpdict = simplejson.loads(mock_nagios_results(type='http'))
        self.assertEquals(pingdict['decoded']['human'], "PING OK - Packet loss = 0%, RTA = 0.11 ms")
        self.assertEquals(httpdict['decoded']['human'], "HTTP OK HTTP/1.0 200 OK - 5825 bytes in 2.158 seconds ")
    #
    def test_functional_storing_results(self):
        """testing storing monitoring data and verifying underlying files"""
        # pylint: disable=E1101
        clear_all_rrd_files()
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "test monitor"
        newmonitor.save()
        datastore_list = newmonitor.datastore_set.all()
        self.assertEquals(len(datastore_list), 0)
        # create mock results - for a ping - 2 values
        mock_result_json = mock_nagios_results(type='ping')
        newmonitor.store_json_results(mock_result_json, debug=False)
        # store and verify new datastore files are created
        datastore_list = newmonitor.datastore_set.all()
        self.assertEquals(len(datastore_list), 2)
        
        # get individial datastores and verify aspects of them - 'pl' and 'rta'
        (datastore1, created_newds) = Datastore.objects.get_or_create(monitor=newmonitor, name='pl')
        self.assertFalse(created_newds)
        self.assertTrue(datastore1)
        self.assertEquals(datastore1.name, 'pl')
        self.assertTrue(datastore1.rrd_exists)
        #mode='r' is a slow method - loads data from the RRD file
        rrd1 = RRD(datastore1.location, mode="r")
        self.assertTrue(rrd1)
        # self.assertEquals(len(rrd1.ds), 1)
        # data_dict1 = rrd1.ds[0].getData()
        # self.assertEquals(data_dict1['name'], 'pl')
        
        # get data for 'rta'
        (datastore2, created_newds) = Datastore.objects.get_or_create(monitor=newmonitor, name='rta')
        self.assertFalse(created_newds)
        self.assertTrue(datastore2)
        self.assertEquals(datastore2.name, 'rta')
        self.assertTrue(datastore2.rrd_exists)
        #mode='r' is a slow method - loads data from the RRD file
        rrd2 = RRD(datastore2.location, mode="r")
        self.assertTrue(rrd2)
        # self.assertEquals(len(rrd2.ds), 1)
        # data_dict2 = rrd2.ds[0].getData()
        # self.assertEquals(data_dict2['name'], 'rta')
        
        # wipe out the RRD files and verify property is working
        clear_all_rrd_files()
        self.assertFalse(datastore1.rrd_exists)
        self.assertFalse(datastore2.rrd_exists)
        #from pyrrd.rrd import RRD, RRA, DS

    def test_failed_store_dict_results(self):
        """ verify failure mode for invalid dict structure"""
        clear_all_rrd_files()
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "test monitor"
        newmonitor.save()
        
        bad_result_dict = { 'a' : 1 }
        store_result = newmonitor.store_dict_results(bad_result_dict)
        self.assertFalse(store_result)

    def test_failed_store_dict_results_debug(self):
        """ verify failure mode for invalid dict structure"""
        clear_all_rrd_files()
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "test monitor"
        newmonitor.save()

        bad_result_dict = { 'a' : 1 }
        store_result = newmonitor.store_dict_results(bad_result_dict, debug=True)
        self.assertFalse(store_result)
