import os
import datetime
import simplejson
from core.models import Datastore
from core.models import Monitor
from core.models import Host
from settings import RRDFILE_ROOT
#
def create_unsaved_minimum_monitor():
    """ creates a basic, but unsaved, monitor. 
    Basic usage in monitor test case:
    
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        newmonitor = create_unsaved_minimum_monitor()
        newmonitor.name = "some monitor name"
        newmonitor.save()
    
    """
    newmonitor = Monitor()
    newmonitor.name = "newmonitor"
    newmonitor.kind = "check_ping"
    return newmonitor
#
def create_unsaved_minimum_host():
    """ creates a basic, but unsaved, host. 
    Basic usage in monitor test case:
    
        from django.core import management
        management.call_command('flush', verbosity=0, interactive=False)
        host = create_unsaved_minimum_host()
        host.hostname = "some hostname"
        host.save()
    
    """
    newhost = Host()
    newhost.hostname = "localhost"
    return newhost
#
def create_unsaved_datastore():
    "helped that creates a monitor and new datastore (datastore unsaved)"
    mon = create_unsaved_minimum_monitor()
    mon.save()
    new_ds = Datastore()
    new_ds.name = "pl"
    new_ds.monitor = mon
    return new_ds
#
def clear_all_rrd_files():
    """nukes all existing RRD files - cleanup for tests"""
    # Delete all reachable .rrd files from the directory named in "RRDFILE_ROOT",
    # assuming there are no symbolic links.
    for root, dirs, files in os.walk(RRDFILE_ROOT, topdown=False):
        for name in files:
            if name.endswith('rrd'):
                os.remove(os.path.join(root, name))
#
def mock_nagios_results(type='ping'):
    """ creates mock results from nagios pollers
    default, type='ping'
    also: type='http'
    """
    ping_dict = {'command': '/opt/local/libexec/nagios/check_ping -H localhost -w 1,99% -c 1,99%', \
     'decoded': {'human': 'PING OK - Packet loss = 0%, RTA = 0.11 ms', \
                 'pl': {'UOM': '%', \
                        'critvalue': '99', \
                        'label': 'pl', \
                        'maxvalue': '', \
                        'minvalue': '0', \
                        'value': '0', \
                        'warnvalue': '99'}, \
                 'rta': {'UOM': 'ms', \
                         'critvalue': '1.000000', \
                         'label': 'rta', \
                         'maxvalue': '', \
                         'minvalue': '0.000000', \
                         'value': '0.113000', \
                         'warnvalue': '1.000000'}}, \
     'error': None, \
     'output': 'PING OK - Packet loss = 0%, RTA = 0.11 ms|rta=0.113000ms;1.000000;1.000000;0.000000 pl=0%;99;99;0', \
     'returncode': 0, \
     'timestamp': '2009-11-07T16:43:46.696214'} 
    http_dict = {'command': '/opt/local/libexec/nagios/check_http -H www.google.com -p 80', \
      'decoded': {'human': 'HTTP OK HTTP/1.0 200 OK - 5825 bytes in 2.158 seconds ', \
                  'size': {'UOM': 'B', \
                           'critvalue': '', \
                           'label': 'size', \
                           'maxvalue': '', \
                           'minvalue': '0', \
                           'value': '5825', \
                           'warnvalue': ''}, \
                  'time': {'UOM': 's', \
                           'critvalue': '', \
                           'label': 'time', \
                           'maxvalue': '', \
                           'minvalue': '0.000000', \
                           'value': '2.157739', \
                           'warnvalue': ''}}, \
      'error': None, \
      'output': 'HTTP OK HTTP/1.0 200 OK - 5825 bytes in 2.158 seconds |time=2.157739s;;;0.000000 size=5825B;;;0', \
      'returncode': 0, \
      'timestamp': '2009-11-07T16:43:48.985950'}
    http_dict['timestamp'] = datetime.datetime.now().isoformat()
    ping_dict['timestamp'] = datetime.datetime.now().isoformat()
    if type == 'http':
        return simplejson.dumps(http_dict)
    return simplejson.dumps(ping_dict)
#