"""Unit tests for pollers, utility module, etc"""
from django.test import TestCase
from util.monitor import MonitorResult
from util.monitor import validate_poller_results
import os

class MointorResultTests(TestCase):
    def test_MonitorResult_UOM_parser(self):
        input = "0.182000ms"
        result = MonitorResult.UOM_PARSECODE.match(input)
        results = result.groups()
        self.assertEqual('0.182000', results[0])
        self.assertEqual('ms', results[1])
        input = "1ms"
        result = MonitorResult.UOM_PARSECODE.match(input)
        results = result.groups()
        self.assertEqual('1', results[0])
        self.assertEqual('ms', results[1])
        input = "1.11"
        result = MonitorResult.UOM_PARSECODE.match(input)
        results = result.groups()
        self.assertEqual('1.11', results[0])
        self.assertEqual('', results[1])
        input = ""
        results = MonitorResult.UOM_PARSECODE.match(input)
        self.assertTrue(results is None)
    #
    def test_MonitorResult_creation(self):
        """ testing creation and initializers for MonitorResult"""
        new_result = MonitorResult()
        self.assertTrue(not(new_result is None))
        self.assertEqual(new_result.command, "")
        self.assertTrue(new_result.error is "")
        self.assertEqual(new_result.returncode, 0)
        self.assertEqual(new_result.decoded, {'_': {'maxvalue': '', 'value': 0, 'minvalue': '', 'UOM': '', 'critvalue': '', 'label': '_', 'warnvalue': ''}, 'human': ''})
        #
        holding_json_string = new_result.json()
        # self.assertEqual(holding_json_string,"")
        self.assertTrue(validate_poller_results(holding_json_string))
        #
        second_result = MonitorResult()
        second_result.loadjson(holding_json_string)
        self.assertEqual(new_result.command, second_result.command)
        self.assertEqual(new_result.error, second_result.error)
        self.assertEqual(new_result.returncode, second_result.returncode)
        self.assertEqual(new_result.decoded, second_result.decoded)
        self.assertEqual(new_result.timestamp.date(), second_result.timestamp.date())
        self.assertEqual(new_result.timestamp.hour, second_result.timestamp.hour)
        self.assertEqual(new_result.timestamp.minute, second_result.timestamp.minute)
        self.assertEqual(new_result.timestamp.second, second_result.timestamp.second)
    #
    def test_MonitorResult_parseoutput(self):
        """ testing parsing code to get Nagios output values into structure"""
        example1 = "PING OK - Packet loss = 0%, RTA = 0.18 ms|rta=0.182000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"
        example2 = "FPING OK - localhost (loss=0%, rta=0.110000 ms)|loss=0%;99;99;0;100 rta=0.000110s;0.001000;0.001000;0.000000"
        example3 = "TCP OK - 0.419 second response time on port 443|time=0.418755s;;;0.000000;10.000000"
        example4 = "HTTP OK HTTP/1.0 200 OK - 10372 bytes in 0.163 seconds |time=0.163247s;;;0.000000 size=10372B;;;0"
        results = MonitorResult.parse_nagios_output(None)
        self.assertTrue(results is None)
        result_dict = MonitorResult.parse_nagios_output(example1)
        self.assertEquals(result_dict['human'], "PING OK - Packet loss = 0%, RTA = 0.18 ms")
        self.assertEquals(len(result_dict.keys()), 3)
        result_dict = MonitorResult.parse_nagios_output(example2)
        self.assertEquals(result_dict['human'], "FPING OK - localhost (loss=0%, rta=0.110000 ms)")
        self.assertEquals(len(result_dict.keys()), 3)
        result_dict = MonitorResult.parse_nagios_output(example4)
        self.assertEquals(result_dict['human'], "HTTP OK HTTP/1.0 200 OK - 10372 bytes in 0.163 seconds ")
        self.assertEquals(len(result_dict.keys()), 3)
        result_dict = MonitorResult.parse_nagios_output(example3)
        self.assertEquals(result_dict['human'], "TCP OK - 0.419 second response time on port 443")
        self.assertEquals(len(result_dict.keys()), 2)
        data_dict = result_dict['time']
        self.assertTrue(data_dict.has_key('label'))
        self.assertEquals(data_dict['label'], 'time')
        self.assertTrue(data_dict.has_key('value'))
        self.assertEquals(data_dict['value'], '0.418755')
        self.assertTrue(data_dict.has_key('UOM'))
        self.assertEquals(data_dict['UOM'], 's')
        self.assertTrue(data_dict.has_key('warnvalue'))
        self.assertEquals(data_dict['warnvalue'], '')
        self.assertTrue(data_dict.has_key('critvalue'))
        self.assertEquals(data_dict['critvalue'], '')
        self.assertTrue(data_dict.has_key('minvalue'))
        self.assertEquals(data_dict['minvalue'], '0.000000')
        self.assertTrue(data_dict.has_key('maxvalue'))
        self.assertEquals(data_dict['maxvalue'], '10.000000')
    #
    def testNagiosParserMonitorResult(self):
        """ testing nagios parsing static method in MonitorResult """
        example1 = "PING OK - Packet loss = 0%, RTA = 0.18 ms|rta=0.182000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"
        example2 = "TCP OK - 0.419 second response time on port 443|time=0.418755s;;;0.000000;10.000000"
        new_dict = MonitorResult.parse_nagios_output(example1)
        self.assertTrue(not(new_dict is None))
        self.assertEqual(new_dict, {'rta': {'maxvalue': '', 'value': '0.182000', 'minvalue': '0.000000', 'UOM': 'ms', 'critvalue': '1.000000', 'label': 'rta', 'warnvalue': '1.000000'}, 'pl': {'maxvalue': '', 'value': '0', 'minvalue': '0', 'UOM': '%', 'critvalue': '99', 'label': 'pl', 'warnvalue': '99'}, 'human': 'PING OK - Packet loss = 0%, RTA = 0.18 ms'})
        self.assertEqual(len(new_dict), 3)
        self.assertEqual(new_dict['human'], 'PING OK - Packet loss = 0%, RTA = 0.18 ms')
        new_dict = MonitorResult.parse_nagios_output(example2)
        self.assertTrue(not(new_dict is None))
        self.assertEqual(new_dict, {'human': 'TCP OK - 0.419 second response time on port 443', 'time': {'maxvalue': '10.000000', 'value': '0.418755', 'minvalue': '0.000000', 'UOM': 's', 'critvalue': '', 'label': 'time', 'warnvalue': ''}})
        self.assertEqual(len(new_dict), 2)
        self.assertEqual(new_dict['human'], 'TCP OK - 0.419 second response time on port 443')
    #
    def testMonitorResultCreateNagios(self):
        example1 = "FPING OK - localhost (loss=0%, rta=0.110000 ms)|loss=0%;99;99;0;100 rta=0.000110s;0.001000;0.001000;0.000000"
        example2 = "HTTP OK HTTP/1.0 200 OK - 10372 bytes in 0.163 seconds |time=0.163247s;;;0.000000 size=10372B;;;0"
        new_result = MonitorResult.createMonitorResultFromNagios(example1)
        self.assertTrue(not(new_result is None))
        self.assertEqual(new_result.command, "")
        self.assertTrue(new_result.error is "")
        self.assertEqual(new_result.returncode, 0)
        self.assertEqual(new_result.decoded, {'loss': {'maxvalue': '100', 'value': '0', 'minvalue': '0', 'UOM': '%', 'critvalue': '99', 'label': 'loss', 'warnvalue': '99'}, 'rta': {'maxvalue': '', 'value': '0.000110', 'minvalue': '0.000000', 'UOM': 's', 'critvalue': '0.001000', 'label': 'rta', 'warnvalue': '0.001000'}, 'human': 'FPING OK - localhost (loss=0%, rta=0.110000 ms)'})
        new_result = MonitorResult.createMonitorResultFromNagios(example2)
        self.assertTrue(not(new_result is None))
        self.assertEqual(new_result.command, "")
        self.assertTrue(new_result.error is "")
        self.assertEqual(new_result.returncode, 0)
        self.assertEqual(new_result.decoded, {'size': {'maxvalue': '', 'value': '10372', 'minvalue': '0', 'UOM': 'B', 'critvalue': '', 'label': 'size', 'warnvalue': ''}, 'human': 'HTTP OK HTTP/1.0 200 OK - 10372 bytes in 0.163 seconds ', 'time': {'maxvalue': '', 'value': '0.163247', 'minvalue': '0.000000', 'UOM': 's', 'critvalue': '', 'label': 'time', 'warnvalue': ''}})

    def testFailedMonitorFromNagiosString(self):
        new_result = None
        try:
            new_result = MonitorResult.createMonitorResultFromNagios(None)
            self.fail("should raise ValueError")
        except ValueError:
            pass
        self.assertTrue(new_result is None)
        try:
            new_result = MonitorResult.createMonitorResultFromNagios("")
            self.fail("should raise ValueError")
        except ValueError:
            pass
        self.assertTrue(new_result is None)

    def testParseNagiosOutputFailureMode(self):
        new_dict = MonitorResult.parse_nagios_output(None)
        self.assertTrue(new_dict is None)
        new_dict = MonitorResult.parse_nagios_output("hello")
        self.assertTrue(new_dict is None)
        nag_string = "hello monkey |size=10372B;;;0" #time=0.163247s;;;0.000000 
        new_dict = MonitorResult.parse_nagios_output(nag_string)
        self.assertEqual(new_dict, {'human': 'hello monkey ', 'size': {'maxvalue': '', 'value': '10372', 'minvalue': '0', 'UOM': 'B', 'critvalue': '', 'label': 'size', 'warnvalue': ''}})
    
    def test_loadjson_validation2(self):
        """ testing positive validation - ping """
        mresult = MonitorResult()
        good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta", "warnvalue": "1.000000"}, "pl": {"maxvalue": "", "value": "0", "minvalue": "0", "UOM": "%", "critvalue": "99", "label": "pl", "warnvalue": "99"}, "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
        mresult.loadjson(good_ping)
        self.assertEqual(mresult.output, "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0")
    #
    def test_loadjson_validation3(self):
        """ testing positive validation - http """
        mresult = MonitorResult()
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult.loadjson(good_http)
        self.assertEqual(mresult.output, "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0")
    #
    def test_loadjson_validation4(self):
        """ testing negative validation - http with list instead of dictionary"""
        bad_http = '["decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"]'
        mresult = MonitorResult()
        try:
            mresult.loadjson(bad_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation5(self):
        """ testing negative loadjson - http missing decoded key"""
        good_http = '{"returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation6(self):
        """ testing negative loadjson - http missing command key"""
        bad_http = '{"returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(bad_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation7(self):
        """ testing negative loadjson - http missing returncode key"""
        bad_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(bad_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation8(self):
        """ testing negative loadjson - invalid returncode key: -1"""
        bad_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": -1, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(bad_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation9(self):
        """ testing negative loadjson - invalid returncode key: string"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": "whatever", "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    
    def test_loadjson_validation10(self):
        """ testing negative loadjson - invalid returncode key: 17"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "timestamp": "2009-11-07T17:01:50.584052", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    
    def test_loadjson_validation11(self):
        """ testing negative loadjson - invalid timestamp"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "timestamp": "whats up willis?", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    
    def test_loadjson_validation12(self):
        """ testing negative loadjson - timestamp missing"""
        good_http = '{"command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "returncode": 17, "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    
    def test_loadjson_validation13(self):
        """ testing negative loadjson - decoded isn't a dict"""        
        good_http = '{"decoded": ["size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"], "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    
    def test_loadjson_validation14(self):
        """ testing negative loadjson - decoded missing human"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation15(self):
        """ testing negative loadjson - decoded missing a key other than human"""        
        good_http = '{"decoded": {"human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    
    def test_loadjson_validation16(self):
        """ testing negative loadjson - decoded[] missing maxvalue"""        
        good_http = '{"decoded": {"size": {"value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation17(self):
        """ testing negative loadjson - decoded[] missing value"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation18(self):
        """ testing negative loadjson - decoded[] missing minvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation19(self):
        """ testing negative loadjson - decoded[] missing UOM"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation20(self):
        """ testing negative loadjson - decoded[] missing critvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B",  "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation21(self):
        """ testing negative loadjson - decoded[] missing label"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation22(self):
        """ testing negative loadjson - decoded[] missing warnvalue"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", }, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation23(self):
        """ testing negative loadjson - decoded[value] not a number"""        
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": "foo", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation24(self):
        """ testing against an incorrect class handed in """
        bad_result = '[]'
        mresult = MonitorResult()
        try:
            mresult.loadjson(bad_result)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation25(self):
        """ testing to verify that command exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation26(self):
        """ testing to verify that command is a string/unicode """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "hello", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK"}, "timestamp": "2009-11-07T17:01:50", "command": 32, "returncode": 0, "error": null, "output": "bar"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation27(self):
        """ testing to verify that error exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "returncode": 0, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    #
    def test_loadjson_validation28(self):
        """ testing to verify that returncode exists """
        good_http = '{"decoded": {"size": {"maxvalue": "", "value": "6155", "minvalue": "0", "UOM": "B", "critvalue": "", "label": "size", "warnvalue": ""}, "human": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds ", "time": {"maxvalue": "", "value": "1.454750", "minvalue": "0.000000", "UOM": "s", "critvalue": "", "label": "time", "warnvalue": ""}}, "timestamp": "2009-11-07T17:01:50.584052", "command": "/opt/local/libexec/nagios/check_http -H www.google.com -p 80", "error": null, "output": "HTTP OK HTTP/1.0 200 OK - 6155 bytes in 1.455 seconds |time=1.454750s;;;0.000000 size=6155B;;;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_http)
            self.fail()
        except KeyError:
            pass
    #        
    def test_loadjson_validation29(self):
        """ verify that timestamp key exists"""
    mresult = MonitorResult()
    good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta", "warnvalue": "1.000000"}, "pl": {"maxvalue": "", "value": "0", "minvalue": "0", "UOM": "%", "critvalue": "99", "label": "pl", "warnvalue": "99"}, "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
    try:
        mresult.loadjson(good_ping)
        self.fail()
    except KeyError:
        pass
    #
    def test_loadjson_validation30(self):
        """ verify that output key exists"""
    mresult = MonitorResult()
    good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta", "warnvalue": "1.000000"}, "pl": {"maxvalue": "", "value": "0", "minvalue": "0", "UOM": "%", "critvalue": "99", "label": "pl", "warnvalue": "99"}, "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null}'
    try:
        mresult.loadjson(good_ping)
        self.fail()
    except KeyError:
        pass
    #
    def test_loadjson_validation31(self):
        """ verify that decoded key is a dictionary"""
    mresult = MonitorResult()
    good_ping = '{"decoded": [ 1, 2 ], "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
    try:
        mresult.loadjson(good_ping)
        self.fail()
    except ValueError:
        pass
    #
    def test_loadjson_validation32(self):
        """ verify that human key in decoded dictionary is a string """
    mresult = MonitorResult()
    good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta", "warnvalue": "1.000000"}, "pl": {"maxvalue": "", "value": "0", "minvalue": "0", "UOM": "%", "critvalue": "99", "label": "pl", "warnvalue": "99"}, "human": 123}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
    try:
        mresult.loadjson(good_ping)
        self.fail()
    except ValueError:
        pass
    #
    def test_loadjson_validation33(self):
        """ testing negative loadjson - decoded missing warnvalue"""        
        good_ping = '{"decoded": {"rta": {"maxvalue": "", "value": "0.119000", "minvalue": "0.000000", "UOM": "ms", "critvalue": "1.000000", "label": "rta"}, "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_ping)
            self.fail()
        except ValueError:
            pass
    #
    def test_loadjson_validation34(self):
        """ testing negative loadjson - decoded dictionary isn't a dictionary"""        
        good_ping = '{"decoded": {"pl": "whats up doc?", "human": "PING OK - Packet loss = 0%, RTA = 0.12 ms"}, "returncode": 0, "timestamp": "2009-11-07T17:01:49.074447", "command": "/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%", "error": null, "output": "PING OK - Packet loss = 0%, RTA = 0.12 ms|rta=0.119000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0"}'
        mresult = MonitorResult()
        try:
            mresult.loadjson(good_ping)
            self.fail()
        except ValueError:
            pass
    #
