from django.test import TestCase
from util.nagios import NagiosPoller
from util.monitor import ArgSet
import os
import datetime

class NagiosInvokerTests(TestCase):
    """ test methods for NagiosPoller"""
    # def setUp(self):
    #     pass
    
    def test_defaults(self):
        """ checking NagiosPoller default values"""
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        local_plugin_directory = xyz.plugin_dir
        self.assertTrue(os.path.exists(local_plugin_directory), "local path for nagios plugins (%s) exists" % local_plugin_directory )
        self.assertEquals(xyz.poller_kind, 'eyeswebapp.util.nagios.NagiosPoller')

    def test_plugin_list(self):
        """functional test to validate that load plugins works"""
        xyz = NagiosPoller()
        result_list = xyz.plugin_list()
        # verify result is a list
        self.assertEquals(type([]), type(result_list))
        # verify that the result has at least four entries...
        self.assertTrue(len(result_list)>4)
        xyz.plugin_dir = "/tmp"
        xyz._load_plugin_list()
        self.assertEquals(len(xyz.plugin_list()), 0)
        
    def test_basicplugins(self):
        """functional test to validate basic plugins exist"""
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        resulting_plugin_list = xyz.plugin_list()
        self.assertTrue("check_ping" in resulting_plugin_list)
        self.assertTrue("check_http" in resulting_plugin_list)
        self.assertTrue("check_tcp" in resulting_plugin_list)
        self.assertTrue("check_snmp" in resulting_plugin_list)

    def test_uom_parser(self):
        """testing internal to the UOM parser to pull out unit of measure"""
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        input = "0.182000ms"
        result = xyz.uom_parsecode.match(input)
        results = result.groups()
        self.assertEqual('0.182000', results[0])
        self.assertEqual('ms', results[1])
        input = "1ms"
        result = xyz.uom_parsecode.match(input)
        results = result.groups()
        self.assertEqual('1', results[0])
        self.assertEqual('ms', results[1])
        input = "1.11"
        result = xyz.uom_parsecode.match(input)
        results = result.groups()
        self.assertEqual('1.11', results[0])
        self.assertEqual('', results[1])
        input = ""
        results = xyz.uom_parsecode.match(input)
        self.assertTrue(results is None)

    def test_functional_invoke_help(self):
        """functional test of check_ping invoked with plugin_help"""
        xyz = NagiosPoller()
        result = xyz.plugin_help('check_ping')
        self.assertTrue(result)
        self.assertEquals(result.returncode, 0)
        self.assertTrue(result.output.startswith("check_ping v"))
        self.assertEqual(result.error, "")
        
    def test_functional_invokehelp_missing_plugin(self):
        """functional test of chubacabra --help (non-exist plugin)"""
        xyz = NagiosPoller()
        mon_result = xyz.plugin_help('chubacabra')
        self.assertTrue(mon_result)
        self.assertEquals(mon_result.command, "")
        self.assertEquals(mon_result.output, "")
        self.assertEquals(mon_result.error, 'No plugin named chubacabra found.')
        
    def test_functional_invoke_invokeNone(self):
        """verifying failure mode for invoking on None"""
        xyz = NagiosPoller()
        result = xyz._invoke(None, None)
        self.assertTrue(result is None)
                
    def test_functional_direct_invoke_help(self):
        """functional test of check_ping --help"""
        xyz = NagiosPoller()
        argset = ArgSet()
        argset.add_argument('--help')
        result = xyz._invoke('check_ping', argset.list_of_arguments())
        self.assertTrue(result)
        self.assertEquals(result.returncode, 0)
        self.assertTrue(result.output.startswith("check_ping v"))
        self.assertEqual(result.error, "")

    def test_functional_checkping1(self):
        """functional test of check_ping against localhost"""
        # root@ubuntu:/usr/lib/nagios/plugins# ./check_ping -H localhost -w 1,99% -c 1,99%
        #PING OK - Packet loss = 0%, RTA = 0.06 ms|rta=0.056000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        ping_argset = ArgSet()
        ping_argset.add_argument_pair("-H", "localhost")
        ping_argset.add_argument_pair("-w", "1,99%")
        ping_argset.add_argument_pair("-c", "1,99%")
        result = xyz._invoke("check_ping", ping_argset.list_of_arguments())
        self.assertTrue(result)
        self.assertEquals(result.returncode, 0)
        self.assertTrue(result.output.startswith("PING OK -"))
        self.assertEqual(result.error, "")
        # now check the output...
        result_dict = result.decoded
        self.assertTrue(result_dict)
        self.assertTrue(result_dict.has_key('human'))
        self.assertTrue(result_dict.has_key('pl'))
        self.assertTrue(result_dict.has_key('rta'))
        self.assertTrue(result_dict['human'].startswith('PING OK'))
        self.assertTrue(result_dict['pl'].has_key('label'))
        self.assertEquals(result_dict['pl']['label'], 'pl')
        self.assertEquals(result_dict['pl']['value'], '0')
        self.assertEquals(result_dict['pl']['UOM'], '%')
        self.assertTrue(result_dict['rta'].has_key('label'))
        self.assertEquals(result_dict['rta']['label'], 'rta')
        self.assertEquals(result_dict['rta']['UOM'], 'ms')

    def test_functional_checkhttp1(self):
        """functional check of check_http against http://www.google.com/ """
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        http_argset = ArgSet()
        http_argset.add_argument_pair("-H", "www.google.com")
        http_argset.add_argument_pair("-p", "80")
        mon_result = xyz.run_plugin('check_http', http_argset)
        self.assertTrue(mon_result)
        self.assertEquals(mon_result.returncode, 0)
        self.assertTrue(mon_result.output.startswith("HTTP OK:"))
        self.assertEqual(mon_result.error, "")
        decoded_dict = mon_result.decoded
        self.assertTrue(decoded_dict, "decoded data is null - expected a dictionary")
        self.assertTrue(decoded_dict.has_key('human'))
        self.assertTrue(decoded_dict.has_key('size'))
        self.assertTrue(decoded_dict.has_key('time'))
        self.assertTrue(decoded_dict['human'].startswith('HTTP OK'))
        self.assertTrue(decoded_dict['size'].has_key('label'))
        self.assertEquals(decoded_dict['size']['label'], 'size')
        self.assertEquals(decoded_dict['size']['UOM'], 'B')
        self.assertTrue(decoded_dict['time'].has_key('label'))
        self.assertEquals(decoded_dict['time']['UOM'], 's')

    def test_functional_checkhttp2(self):
        """ functional check of check_http against a non-existant hostname """
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        http_argset = ArgSet()
        http_argset.add_argument_pair("-H", "nothing.local")
        mon_result = xyz.run_plugin('check_http', http_argset)
        # and check the results...
        self.assertTrue(mon_result)
        # check contents for having something, or not...
        self.assertEquals(mon_result.returncode, 2) # critical error
        self.assertEqual(mon_result.error, "")

    def test_functional_checkping_empty_argset(self):
        """ functional check of check_ping with empty argset """
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        mon_result = xyz.run_plugin('check_ping')
        # and check the results...
        self.assertTrue(mon_result)
        # check contents for having something, or not...
        self.assertEquals(mon_result.returncode, 3) # critical error
        self.assertEqual(mon_result.error, "")

    def test_functional_checkping_invalid_argset(self):
        """ functional check of check_ping with invalid argset """
        xyz = NagiosPoller()
        self.assertTrue(xyz)
        invalid_argset = ArgSet()
        invalid_argset.add_argument_pair("-WhoKnowsWhat", "invalid values 123")
        mon_result = xyz.run_plugin('check_ping', invalid_argset)
        # and check the results...
        self.assertTrue(mon_result)
        self.assertEquals(mon_result.returncode, 3) # unknown result
