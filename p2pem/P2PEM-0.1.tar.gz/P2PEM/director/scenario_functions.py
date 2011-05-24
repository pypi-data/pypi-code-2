


PEER_IDENT_MODE = 'id'
"""
    Peer identification mode.
    values:
        'id' - e.g. "12-25"
        'ip' - e.g. "10.0.1.10-26"
"""


DIR_LOG = {}
"""
    Dictionary with settings of Director log.
    default value:
        DIR_LOG = {'mode':{'file':'debug', 'console':'info'}, 'file_name':'director.log'}
    dict keys:
        'mode' - dict, enabled handlers as keys, logging levels as values
        'file_name' - if 'file' handler enabled, sets the log file name
"""
SWAP_LIMIT = 100
"""
    Swap limit in KB. When reached, swapping logged as warning.
"""


MAN_TO_DIR_LOG_ADDR = None
"""
    If Manager logging to Director enabled this IP address will be used to listen to the log messages from Managers.
    If not set, the "Manager to Director" logging will not be established.
"""

MAN_TO_DIR_LOG_PORT = 11111
"""
    If Manager logging to Director enabled this port will be used to listen to the log messages from Managers.
"""



def setstatsnopeer(director, all='', up='', down=''):
    director.set_no_peer_stats(all, up, down)
    """
    Sets IP addresses from parameters to be monitored. Use only for peers not managed by Managers.
    Only already shaped ip addresses will be monitored.
    params:
        all - ip range/ip range, upload and download will be monitored
        up - ip range/ip range, upload will be monitored
        down - id range/ip range, download will be monitored
    """  
    
def setstats(director, all='', up='', down=''):
    director.set_stats(all, up, down)
    """
    Sets peers from parameters to be monitored. Use only for peers managed by Managers.
    Only already shaped peers will be monitored.
    params:
        all - id range/ip range, upload and download will be monitored
        up - id range/ip range, upload will be monitored
        down - id range/ip range, download will be monitored
    """      

def startstats(director, timeout):
    director.start_shaped_stats(timeout)
    """
    Starts gathering of statistics. The statistics will be collected for all set peers
    and ip addresses every defined perion of time (timeout). Fails if already started.
    params:
        timeout - float
    """
    
def stopstatsreport(director, file_name):
    director.stop_shaped_stats_and_report(file_name)
    """
    Stops gathering of statistics and generates the report. Fails if statistics are not running.
    params:
        file_name - string, name of the report file, created if does not exist
    """
def stopstats(director):
    """
    Stops statistics on all managers.
    """
    director.stop_shaped_stats()
    
def statsreport(director, file_name):
    director.generate_stats_report(file_name)
    """
    Generates the report file with collected statistics. Fails if statistics are not stopped.
    params:
        file_name - string, name of the report file, created if does not exist
    """
    
def statssetformat(director, format_name):
    director.shaped_stats_set_report_format(format_name)
    """
    Sets the report format "format_name" as active. Fails if report the format name is not defined.
    params:
        format_name - string, name of the report format to be set
    """
    
def resetall(director):
    director.reset_all()
    """
    Resets the whole testing environment: all Managers, running peers, traffic shaping, statistics ...
    All data collected by statistics are lost.
    """
    
def resetmachine(director, manager):
    director.reset_manager(manager)
    """
    Resets the Manager: running peers, traffic shaping ...
    May not be used when collecting statistics.
    params:
        manager - manager id
    """
    
def sleep(director, seconds):
    director.sleep_for(seconds)
    """
    Stops the scenario execution for "seconds".
    params:
        seconds - int
    """

def create(director, manager, id_range, *args):
    director.create_peers(manager, id_range, *args)
    """
    Creates peers on Manager "manager.
    params:
        manager - manager id
        id_range - id range/ip range
        args - list of arguments, user defined
    """
 
def killhard(director, id_range):
    director.kill_hard(id_range)
    """
    Sends SIG_KILL to peers.
    params:
        id_range - id range/ip range 
    """

def killhrandom(director, manager, number):
    director.kill_hard_random(manager, number)
    """
    Sends SIG_KILL to "number" of random peers on Manager "manager".
    params:
        manager - manager id
        number - int, number of peers to be killed
    """

def killsoft(director, id_range):
    director.kill_soft(id_range)
    """
    Sends SIG_TERM to peers.
    params:
        id_range - id range/ip range 
    """
    
def killsrandom(director, manager, number):
    director.kill_soft_random(manager, number)
    """
    Sends SIG_TERM to "number" of random peers on Manager "manager".
    params:
        manager - manager id
        number - int, number of peers to be killed
    """

def swapcontrol(director, manager):
    director.swap_control(manager)
    """
    Logs swap space usage of Manager "manager".
    params:
        manager - manager id
    """
    
def swapall(director):
    director.swap_control_all()
    """
    Logs swap space usage of all Managers.
    """

def definerandomshape(director, delay, upload, download):
    """
    Allows to define limits for random shaping.
    When called again resets the limits.
    params:
    all params are tuples (min, max)
        delay - delay limits in ms, default (0, 200)
        upload - peer upload limits in Kb/s, default (100, 5000)
        download - peer download limits in Kb/s, default (300, 10000)
    """
    director.define_random_shape(delay, upload, download)

def shaperandom(director, id_range):
    """
    Shapes peers using random values from defined limits by
    definerandomshape or default values.
    params:
        id_range - id range/ip range
    """
    director.shape_random(id_range)

def shaperandomnonpeer(director, manager, ip_range):
    """
    Shapes peers not manager by Managers using random values
    from defined limits by definerandomshape or default values.
    params:
        manager - manager id
        ip_range - ip range
    """
    director.shape_random_non_peer(manager, ip_range)

def shape(director, delay, upload, download, id_range):
    director.shape(delay, upload, download, id_range)
    """
    Sets traffic shaping of peers. Peer does have to be running,
    but must be inicialized somewhere in the scenario.
    params:
        delay - int, peer delay in ms
        upload - int, peer upload limit in Kb/s
        download - int, peer download limit in Kb/s
        id_range - id range/ip range
    """
    

def shapenonpeer(director, manager, delay, upload, download, ip_range):
    director.shape_non_peer(manager, delay, upload, download, ip_range)
    """
    Sets traffic shaping of IP addresses. Use only for peers not managed by Managers.
    params:
        manager - manager id
        delay - int, peer delay in ms
        upload - int, peer upload limit in Kb/s
        download - int, peer download limit in Kb/s
        ip_range - ip range
    """

def signal(director, signal, id_range):
    """
    Sends signal to peers.
    Do not use to send SIG_TERM or SIG_KILL, use killsoft and killhard instead.
    params:
        id range - id_range/ip_range
        signal - subprocess.signal
    """
    director.send_signal_to_peers(id_range, signal)
    
def command(director, command, id_range):
    """
    Sends command to peers.
    params:
        id_range - id_range/ip_range
        command - string
    """
    director.send_command_to_peers(id_range, command)

scenario = ()
 
import sys, os
sys.path.append(os.getcwd())
try:
    from tor_scenario_functions import *
except:
    pass