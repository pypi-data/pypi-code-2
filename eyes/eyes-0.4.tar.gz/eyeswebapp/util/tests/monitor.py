from django.test import TestCase
from util.monitor import MonitoringPoller
from util.monitor import validate_poller_results

class MonitoringPollerTests(TestCase):
    
    def test_default_property(self):
        """ verify base property of BaseClass for pollers"""
        x = MonitoringPoller()
        self.assertEquals(x.poller_kind,'eyeswebapp.util.baseclass')
    
    def test_not_implemented_run_plugin(self):
        """ verify Not Implemented for run_plugin """
        x = MonitoringPoller()
        self.assertRaises(NotImplementedError, x.run_plugin, None, None )
        self.assertRaises(NotImplementedError, x.run_plugin, None )
        self.assertRaises(TypeError, x.run_plugin )

    def test_not_implemented_plugin_help(self):
        """ verify Not Implemented for plugin_help """
        x = MonitoringPoller()
        self.assertRaises(NotImplementedError, x.plugin_help, None )
        self.assertRaises(TypeError, x.plugin_help )

    def test_plugin_list(self):
        """ verify default impl for plugin_list """
        x = MonitoringPoller()
        self.assertEquals(None, x.plugin_list() )

class PollerOutputValidationTests(TestCase):
    def test_poller_validation1(self):
        """ verify basic false validations """
        self.assertFalse(validate_poller_results(None))
        self.assertFalse(validate_poller_results(''))

    def test_poller_validation2(self):
        """ testing positive validation - ping """
        good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta", "warnvalue": "1.000000"}, "pl": {"maxvalue": "", "value": "0", "minvalue": "0", "UOM": "%", "critvalue": "99", "label": "pl", "warnvalue": "99"}, "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
        ping_result = validate_poller_results(good_ping)
        self.assertTrue(ping_result)

    def test_poller_validation3(self):
        """ testing positive validation - http """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertTrue(http_result)

    def test_poller_validation4(self):
        """ testing negative validation - http with list instead of dictionary"""
        good_http = '["decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"]'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation5(self):
        """ testing negative validation - http missing decoded key"""
        good_http = '{"returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation6(self):
        """ testing negative validation - http missing command key"""
        good_http = '{"returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation7(self):
        """ testing negative validation - http missing returncode key"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation8(self):
        """ testing negative validation - invalid returncode key: string"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": "whatever", "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation9(self):
        """ testing negative validation - invalid returncode key: 17"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation10(self):
        """ testing negative validation - invalid timestamp"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "timestamp": "whats up willis?", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation11(self):
        """ testing negative validation - timestamp missing"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation12(self):
        """ testing negative validation - decoded isn't a dict"""        
        good_http = '{"decoded": ["size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"], "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation13(self):
        """ testing negative validation - decoded missing human"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation14(self):
        """ testing negative validation - decoded missing a key other than human"""        
        good_http = '{"decoded": {"human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)

    def test_poller_validation15(self):
        """ testing negative validation - decoded[] missing maxvalue"""        
        good_http = '{"decoded": {"size": {"value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation16(self):
        """ testing negative validation - decoded[] missing value"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation17(self):
        """ testing negative validation - decoded[] missing minvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation18(self):
        """ testing negative validation - decoded[] missing UOM"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation19(self):
        """ testing negative validation - decoded[] missing critvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B",  "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation20(self):
        """ testing negative validation - decoded[] missing label"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation21(self):
        """ testing negative validation - decoded[] missing warnvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", }, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation22(self):
        """ testing negative validation - decoded[value] not a number"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation23(self):
        """ testing against an incorrect class handed in """
        bad_result = '[]'
        result = validate_poller_results(bad_result)
        self.assertFalse(result)
    #
    def test_poller_validation24(self):
        """ testing to verify that command exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation25(self):
        """ testing to verify that command is a string/unicode """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": 32, "returncode": 0, "error": null, "output": "bar"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation26(self):
        """ testing to verify that error exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation27(self):
        """ testing to verify that returncode exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
    #
    def test_poller_validation28(self):
        """ testing negative validation - invalid returncode key: -1"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": -1, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        http_result = validate_poller_results(good_http)
        self.assertFalse(http_result)
